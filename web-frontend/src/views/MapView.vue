<template>
  <div class="map-page">
    <!-- 顶部标题区域：采用与首页完全一致的 1040px 规范 -->
    <header class="header-section">
      <h2 class="page-title">流散文物全球地理分布图</h2>
      
      <!-- 红色标签：靠右绝对定位，空间充足，绝不换行 -->
      <el-tag size="large" type="danger" effect="dark" class="status-tag">
        <el-icon class="tag-icon"><Compass /></el-icon>
        <span class="tag-text">动态追踪海外藏中国文物</span>
      </el-tag>
    </header>

    <!-- 地图主区域：1040px 约束 -->
    <section class="map-section">
      <div class="map-wrapper">
        <div id="leaflet-map"></div>
        
        <!-- 悬浮控制面板 -->
        <div class="floating-panel">
          <div class="panel-item">
            <div class="label">覆盖海外国家</div>
            <div class="value">15+ <span class="unit">个</span></div>
          </div>
          <div class="panel-item">
            <div class="label">精准标点机构</div>
            <div class="value">{{ museums.length }} <span class="unit">家</span></div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Compass } from '@element-plus/icons-vue';
import { getMuseumMapData } from '../api/mockService.js';

const museums = ref([]);
let map = null;

const fixLeafletIcon = () => {
  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  });
};

const initMap = async () => {
  fixLeafletIcon();
  
  map = L.map('leaflet-map', {
    zoomControl: false,
    minZoom: 2
  }).setView([28, 20], 3);

  L.control.zoom({ position: 'bottomright' }).addTo(map);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO'
  }).addTo(map);

  try {
    const res = await getMuseumMapData();
    if (res.code === 200) {
      museums.value = res.data;
      
      museums.value.forEach(museum => {
        if (museum.latitude && museum.longitude) {
          const popupContent = `
            <div class="custom-map-popup">
              <h4>${museum.nameZh || museum.name}</h4>
              <div class="popup-row"><b>机构驻地:</b> <span>${museum.country} · ${museum.city}</span></div>
              <div class="popup-count">
                <span>馆藏中国文物量</span>
                <strong>${museum.artifactCount.toLocaleString()} 件</strong>
              </div>
            </div>
          `;

          L.marker([museum.latitude, museum.longitude])
            .addTo(map)
            .bindPopup(popupContent, { maxWidth: 300, className: 'modern-popup-style' });
        }
      });
    }
  } catch (error) {
    console.error("加载地图数据失败", error);
  }
};

onMounted(() => {
  initMap();
});
</script>

<style scoped>
.map-page {
  min-height: 100vh;
  background: #f5f7fb; /* 完美的首页底色 */
  padding: 32px 0 60px;
  box-sizing: border-box;
  width: 100%;
}

/* 头部样式：严格对标首页宽度与层级 */
.header-section {
  width: 1040px;
  margin: 0 auto 24px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 40px;
}

/* 标题样式：百分百同步首页精选文物二级标题 */
.page-title {
  text-align: center;
  margin: 0;
  font-size: 28px;
  font-weight: 500;
  color: #000000;
}

/* 标签样式：采用绝对定位锚定右侧，不占空间 */
.status-tag {
  position: absolute;
  right: 0;
  font-weight: 600;
  border-radius: 8px;
  padding: 0 16px;
  height: 38px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: none;
}

.tag-icon {
  font-size: 16px;
}

.tag-text {
  line-height: 1;
}

/* 地图区块布局控制 */
.map-section {
  width: 1040px;
  margin: 0 auto;
}

.map-wrapper {
  position: relative;
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
}

#leaflet-map {
  width: 100%;
  height: 680px; 
  background: #e5e7eb;
}

/* 悬浮面板：防止换行缩进 */
.floating-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(8px);
  padding: 14px 20px;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  display: flex;
  gap: 24px;
}

.panel-item {
  display: flex;
  flex-direction: column;
  white-space: nowrap;
}

.panel-item .label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 4px;
}

.panel-item .value {
  font-size: 22px;
  font-weight: 700;
  color: #203f73; /* 使用和首页一致的经典深蓝 */
}

.panel-item .unit {
  font-size: 13px;
  font-weight: normal;
  color: #909399;
}

/* 响应式媒体查询：完全复制首页的 1100px 与 800px 规则 */
@media screen and (max-width: 1100px) {
  .header-section,
  .map-section {
    width: calc(100% - 48px);
  }
}

@media screen and (max-width: 800px) {
  .header-section {
    flex-direction: column;
    gap: 12px;
    min-height: auto;
  }
  .status-tag {
    position: static;
  }
}
</style>

<style>
/* Leaflet 内部样式未变更 */
.modern-popup-style .leaflet-popup-content-wrapper {
  border-radius: 12px;
  padding: 6px;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
}
.custom-map-popup h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #7f1d1d; 
  border-bottom: 1px solid #fee2e2;
  padding-bottom: 6px;
}
.custom-map-popup .popup-row {
  font-size: 12px;
  color: #475569;
  margin: 4px 0;
}
.custom-map-popup .popup-count {
  margin-top: 12px;
  background: #fef2f2;
  padding: 8px 12px;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.custom-map-popup .popup-count span {
  font-size: 11px;
  color: #991b1b;
}
.custom-map-popup .popup-count strong {
  font-size: 15px;
  color: #b91c1c;
}
</style>