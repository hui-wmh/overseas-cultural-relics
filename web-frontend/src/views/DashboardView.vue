<template>
  <div class="dashboard-page">
    <!-- 引入 dashboard-section 作为统一的 1040px 容器 -->
    <div class="dashboard-section">
      
      <!-- 顶级核心指标卡片 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :xs="24" :sm="12">
          <div class="gradient-card card-museums">
            <div class="card-inner">
              <div class="meta-title">已连接海外机构总量</div>
              <div class="meta-value">
                {{ statsData.summary.totalMuseums.toLocaleString() }} <span class="unit">家</span>
              </div>
            </div>
            <div class="card-bg-icon">🏛️</div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12">
          <div class="gradient-card card-artifacts">
            <div class="card-inner">
              <div class="meta-title">已收录流散中国文物总数</div>
              <div class="meta-value">
                {{ statsData.summary.totalArtifacts.toLocaleString() }} <span class="unit">件</span>
              </div>
            </div>
            <div class="card-bg-icon">🏺</div>
          </div>
        </el-col>
      </el-row>

      <!-- 中部可视化图表区域 -->
      <el-row :gutter="20" style="margin-top: 24px;">
        <el-col :xs="24" :lg="10">
          <el-card shadow="never" class="chart-card">
            <div ref="typeChartRef" style="width: 100%; height: 380px;"></div>
          </el-card>
        </el-col>
        <el-col :xs="24" :lg="14">
          <el-card shadow="never" class="chart-card">
            <div ref="museumChartRef" style="width: 100%; height: 380px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 底部时空跨度走势大图 -->
      <el-row :gutter="20" style="margin-top: 24px;">
        <el-col :span="24">
          <el-card shadow="never" class="chart-card">
            <div ref="dynastyChartRef" style="width: 100%; height: 400px;"></div>
          </el-card>
        </el-col>
      </el-row>
      
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive, nextTick } from 'vue';
import * as echarts from 'echarts';
import { getDashboardStats } from '../api/mockService.js';

const typeChartRef = ref(null);
const museumChartRef = ref(null);
const dynastyChartRef = ref(null);

const statsData = reactive({
  summary: { totalArtifacts: 0, totalMuseums: 0 },
  types: [],
  dynasties: [],
  museums: []
});

const loadDataAndInitCharts = async () => {
  try {
    const res = await getDashboardStats();
    if (res.code === 200) {
      Object.assign(statsData, res.data);
      await nextTick();

      // 1. 文物类型占比饼图
      const typeChart = echarts.init(typeChartRef.value);
      typeChart.setOption({
        title: { text: '文物类型构成占比', left: '0', textStyle: { color: '#000000', fontSize: 16, fontWeight: '500' } },
        tooltip: { trigger: 'item', formatter: '{b} : {c} ({d}%)' },
        legend: { orient: 'vertical', right: '0', top: 'center', itemGap: 12, textStyle: { color: '#606266' } },
        color: ['#bdc3c7', '#95a5a6', '#7f8c8d', '#34495e', '#2c3e50', '#c0392b', '#d35400'], 
        series: [{
          name: '文物类型',
          type: 'pie',
          radius: ['40%', '70%'], 
          center: ['40%', '55%'],
          avoidLabelOverlap: false,
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
          label: { show: false },
          data: statsData.types,
        }]
      });

      // 2. 博物馆藏量排行榜
      const museumChart = echarts.init(museumChartRef.value);
      museumChart.setOption({
        title: { text: '海外顶级博物馆藏量排行', left: '0', textStyle: { color: '#000000', fontSize: 16, fontWeight: '500' } },
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
        xAxis: { 
          type: 'category', 
          data: statsData.museums.map(i => i.name), 
          axisLabel: { rotate: 15, color: '#606266' },
          axisLine: { lineStyle: { color: '#e4e7ed' } }
        },
        yAxis: { type: 'value', name: '数量 (件)', splitLine: { lineStyle: { type: 'dashed', color: '#f5f7fb' } } },
        series: [{
          data: statsData.museums.map(i => i.value),
          type: 'bar',
          barWidth: '35%',
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#203f73' }, /* 统一换成首页的主调深蓝 */
              { offset: 1, color: '#3a5e9e' }  
            ])
          }
        }]
      });

      // 3. 朝代流散分布折线图
      const dynastyChart = echarts.init(dynastyChartRef.value);
      dynastyChart.setOption({
        title: { text: '历史各朝代文物海外流散分布走势', left: '0', textStyle: { color: '#000000', fontSize: 16, fontWeight: '500' } },
        tooltip: { trigger: 'axis' },
        grid: { left: '4%', right: '4%', bottom: '8%', containLabel: true },
        xAxis: { 
          type: 'category', 
          boundaryGap: false, 
          data: statsData.dynasties.map(i => i.name),
          axisLabel: { color: '#606266' }
        },
        yAxis: { type: 'value', splitLine: { lineStyle: { type: 'dashed', color: '#f5f7fb' } } },
        series: [{
          data: statsData.dynasties.map(i => i.value),
          type: 'line',
          smooth: true,
          symbolSize: 8,
          itemStyle: { color: '#7f1d1d' },
          lineStyle: { width: 3, color: '#7f1d1d' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(127, 29, 29, 0.25)' },
              { offset: 1, color: 'rgba(127, 29, 29, 0)' }
            ])
          }
        }]
      });

      window.addEventListener('resize', () => {
        typeChart.resize();
        museumChart.resize();
        dynastyChart.resize();
      });
    }
  } catch (error) {
    console.error("加载图表统计数据失败", error);
  }
};

onMounted(() => {
  loadDataAndInitCharts();
});
</script>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: #f5f7fb; /* 同步首页底色 */
  padding: 32px 0 60px;
  box-sizing: border-box;
  width: 100%;
}

/* 看板核心对齐容器：严格匹配 1040px */
.dashboard-section {
  width: 1040px;
  margin: 0 auto;
}

.gradient-card {
  position: relative;
  border-radius: 12px;
  padding: 28px 32px;
  color: #ffffff;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s;
}

.gradient-card:hover {
  transform: translateY(-2px);
}

.card-museums {
  background: linear-gradient(135deg, #203f73 0%, #3a5e9e 100%); /* 匹配首页主调蓝 */
}

.card-artifacts {
  background: linear-gradient(135deg, #7f1d1d 0%, #b91c1c 100%);
}

.meta-title {
  font-size: 14px;
  opacity: 0.85;
  letter-spacing: 0.5px;
}

.meta-value {
  font-size: 36px;
  font-weight: 700;
  margin-top: 8px;
  line-height: 1.2;
}

.meta-value .unit {
  font-size: 15px;
  font-weight: normal;
  opacity: 0.8;
  margin-left: 4px;
}

.card-bg-icon {
  position: absolute;
  right: -5px;
  bottom: -15px;
  font-size: 90px;
  opacity: 0.12;
  user-select: none;
}

.chart-card {
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  background: #ffffff;
}

/* 响应式断点：百分百同步首页配置 */
@media screen and (max-width: 1100px) {
  .dashboard-section {
    width: calc(100% - 48px);
  }
}

@media screen and (max-width: 768px) {
  .stats-row .el-col {
    margin-bottom: 16px;
  }
}
</style>