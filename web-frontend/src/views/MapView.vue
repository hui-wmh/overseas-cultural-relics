<template>
  <div class="map-page">
    <header class="header-section">
      <h2 class="page-title">流散文物全球地理分布图</h2>

      <el-tag size="large" type="danger" effect="dark" class="status-tag">
        <el-icon class="tag-icon"><Compass /></el-icon>
        <span class="tag-text">动态追踪海外藏中国文物</span>
      </el-tag>
    </header>

    <section class="map-section">
      <div class="map-wrapper">
        <div id="leaflet-map"></div>

        <div class="floating-panel">
          <div class="panel-item">
            <div class="label">覆盖海外国家</div>
            <div class="value">{{ coveredCountryCount }} <span class="unit">个</span></div>
          </div>
          <div class="panel-item">
            <div class="label">标点博物馆</div>
            <div class="value">{{ museums.length }} <span class="unit">家</span></div>
          </div>
          <div class="panel-item">
            <div class="label">平台收录藏品</div>
            <div class="value">{{ formatNumber(totalIndexedArtifacts) }} <span class="unit">件</span></div>
          </div>
        </div>

        <aside v-if="selectedMuseum" class="collection-panel">
          <div class="collection-header">
            <div>
              <div class="panel-kicker">
                <el-icon><OfficeBuilding /></el-icon>
                <span>馆藏机构</span>
              </div>
              <h3>{{ selectedMuseum.nameZh || selectedMuseum.name }}</h3>
              <p>{{ selectedMuseum.name }}</p>
            </div>
            <button class="icon-button" type="button" aria-label="关闭馆藏面板" @click="clearSelection">
              <el-icon><Close /></el-icon>
            </button>
          </div>

          <div class="museum-meta">
            <span>
              <el-icon><LocationFilled /></el-icon>
              {{ selectedMuseum.country || '未知国家' }} · {{ selectedMuseum.city || '未知城市' }}
            </span>
            <a
              v-if="selectedMuseum.website"
              :href="selectedMuseum.website"
              target="_blank"
              rel="noopener noreferrer"
            >
              官网
            </a>
          </div>

          <div class="collection-metrics">
            <div>
              <span>馆藏估算</span>
              <strong>{{ formatNumber(getEstimatedCount(selectedMuseum)) }}</strong>
            </div>
            <div>
              <span>平台收录</span>
              <strong>{{ formatNumber(artifactTotal) }}</strong>
            </div>
          </div>

          <div class="artifact-section-title">
            <el-icon><Collection /></el-icon>
            <span>该馆藏品</span>
          </div>

          <div v-if="loadingArtifacts" class="artifact-loading">
            <div v-for="item in 4" :key="item" class="artifact-skeleton">
              <div></div>
              <section>
                <span></span>
                <span></span>
                <span></span>
              </section>
            </div>
          </div>

          <el-empty
            v-else-if="!museumArtifacts.length"
            description="暂无收录藏品"
            :image-size="72"
          />

          <div v-else class="artifact-list">
            <button
              v-for="artifact in museumArtifacts"
              :key="artifact.id"
              class="artifact-card"
              type="button"
              @click="goArtifactDetail(artifact.id)"
            >
              <img
                :src="artifact.imageUrl"
                :alt="artifact.titleZh"
                @error="handleArtifactImageError($event, artifact.id)"
              />
              <div class="artifact-info">
                <strong>{{ artifact.titleZh || artifact.title }}</strong>
                <span class="artifact-title-en">{{ artifact.title }}</span>
                <span class="artifact-meta">
                  {{ artifact.dynastyName || '暂无朝代' }} · {{ artifact.typeName || '暂无类型' }}
                </span>
                <span class="artifact-period">{{ artifact.period || '暂无年代' }}</span>
              </div>
              <el-icon class="artifact-arrow"><ArrowRight /></el-icon>
            </button>
          </div>
        </aside>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {
  ArrowRight,
  Close,
  Collection,
  Compass,
  LocationFilled,
  OfficeBuilding
} from '@element-plus/icons-vue';
import { getMuseumArtifacts, getMuseumMapData } from '../api/mockService.js';

const router = useRouter();

const museums = ref([]);
const selectedMuseum = ref(null);
const museumArtifacts = ref([]);
const artifactTotal = ref(0);
const loadingArtifacts = ref(false);

let map = null;
let markerLayer = null;
const markerMap = new Map();

const coveredCountryCount = computed(() => {
  return new Set(museums.value.map((museum) => museum.country).filter(Boolean)).size;
});

const totalIndexedArtifacts = computed(() => {
  return museums.value.reduce((sum, museum) => {
    return sum + getIndexedCount(museum);
  }, 0);
});

const getIndexedCount = (museum) => {
  return Number(museum?.indexedArtifactCount ?? museum?.artifactCount ?? 0);
};

const getEstimatedCount = (museum) => {
  return Number(museum?.estimatedArtifactCount ?? museum?.totalArtifactCount ?? museum?.artifactCount ?? 0);
};

const formatNumber = (value) => {
  return Number(value || 0).toLocaleString('zh-CN');
};

const formatMarkerCount = (value) => {
  const count = Number(value || 0);

  if (count >= 10000) {
    return `${Math.round(count / 10000)}万`;
  }

  return count || '0';
};

const escapeHtml = (value) => {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
};

const hasCoordinate = (museum) => {
  return Number.isFinite(Number(museum.latitude)) && Number.isFinite(Number(museum.longitude));
};

const getMarkerGroupKey = (museum) => {
  const country = museum.country || '';
  const city = museum.city || '';

  if (country || city) {
    return `${country}-${city}`;
  }

  return `${Number(museum.latitude).toFixed(1)}-${Number(museum.longitude).toFixed(1)}`;
};

const getMarkerOffset = (index, total) => {
  if (total <= 1) {
    return { x: 0, y: 0 };
  }

  const radius = total === 2 ? 30 : 34;
  const angle = total === 2
    ? (index === 0 ? Math.PI : 0)
    : (-Math.PI / 2) + ((Math.PI * 2 * index) / total);

  return {
    x: Math.round(Math.cos(angle) * radius),
    y: Math.round(Math.sin(angle) * radius)
  };
};

const getMarkerModels = (points) => {
  const groupMap = new Map();

  points.forEach((museum) => {
    const key = getMarkerGroupKey(museum);
    const group = groupMap.get(key) || [];
    group.push(museum);
    groupMap.set(key, group);
  });

  return points.map((museum) => {
    const group = groupMap.get(getMarkerGroupKey(museum)) || [museum];
    const index = group.findIndex((item) => item.id === museum.id);

    return {
      museum,
      offset: getMarkerOffset(index, group.length)
    };
  });
};

const createMuseumIcon = (museum, offset = { x: 0, y: 0 }) => {
  const count = getIndexedCount(museum);

  return L.divIcon({
    className: 'museum-marker-container',
    html: `
      <div class="museum-marker" style="--marker-offset-x: ${offset.x}px; --marker-offset-y: ${offset.y}px;">
        <div class="marker-core">馆</div>
        <div class="marker-count">${escapeHtml(formatMarkerCount(count))}</div>
      </div>
    `,
    iconSize: [52, 58],
    iconAnchor: [26, 48],
    popupAnchor: [0, -44]
  });
};

const createPopupContent = (museum) => {
  return `
    <div class="custom-map-popup">
      <h4>${escapeHtml(museum.nameZh || museum.name)}</h4>
      <div class="popup-row"><b>机构驻地:</b> <span>${escapeHtml(museum.country || '未知')} · ${escapeHtml(museum.city || '未知')}</span></div>
      <div class="popup-count">
        <span>平台收录藏品</span>
        <strong>${escapeHtml(formatNumber(getIndexedCount(museum)))} 件</strong>
      </div>
    </div>
  `;
};

const setActiveMarker = (museumId) => {
  markerMap.forEach((marker, id) => {
    marker.getElement()?.classList.toggle('is-active', id === museumId);
  });
};

const clearSelection = () => {
  selectedMuseum.value = null;
  museumArtifacts.value = [];
  artifactTotal.value = 0;
  setActiveMarker(null);
};

const selectMuseum = async (museum) => {
  selectedMuseum.value = museum;
  museumArtifacts.value = [];
  artifactTotal.value = getIndexedCount(museum);
  loadingArtifacts.value = true;
  setActiveMarker(museum.id);

  if (map && hasCoordinate(museum)) {
    const targetZoom = Math.max(map.getZoom(), 4);
    map.flyTo([museum.latitude, museum.longitude], targetZoom, { duration: 0.45 });
  }

  try {
    const res = await getMuseumArtifacts(museum.id, {
      page: 1,
      pageSize: 100
    });

    if (res.code === 200) {
      const pageData = res.data?.artifacts || res.data || {};
      museumArtifacts.value = pageData.records || [];
      artifactTotal.value = pageData.total ?? museumArtifacts.value.length;
    }
  } catch (error) {
    console.error('加载博物馆藏品失败', error);
  } finally {
    loadingArtifacts.value = false;
  }
};

const addMuseumMarkers = () => {
  markerLayer?.clearLayers();
  markerMap.clear();

  const points = museums.value.filter(hasCoordinate);
  const markerModels = getMarkerModels(points);

  markerModels.forEach(({ museum, offset }) => {
    const marker = L.marker([museum.latitude, museum.longitude], {
      icon: createMuseumIcon(museum, offset),
      riseOnHover: true
    })
      .addTo(markerLayer)
      .bindPopup(createPopupContent(museum), {
        maxWidth: 300,
        className: 'modern-popup-style'
      });

    marker.on('click', () => selectMuseum(museum));
    markerMap.set(museum.id, marker);
  });

  if (points.length) {
    const bounds = L.latLngBounds(points.map((museum) => [museum.latitude, museum.longitude]));
    map.fitBounds(bounds.pad(0.28), {
      maxZoom: 4,
      animate: false
    });
  }
};

const loadMuseumMapData = async () => {
  const res = await getMuseumMapData();

  if (res.code === 200) {
    museums.value = Array.isArray(res.data) ? res.data : res.data?.records || [];
    addMuseumMarkers();
  }
};

const initMap = async () => {
  map = L.map('leaflet-map', {
    zoomControl: false,
    minZoom: 2,
    worldCopyJump: true
  }).setView([32, 18], 3);

  markerLayer = L.layerGroup().addTo(map);

  L.control.zoom({ position: 'bottomright' }).addTo(map);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO'
  }).addTo(map);

  try {
    await loadMuseumMapData();
  } catch (error) {
    console.error('加载地图数据失败', error);
  }
};

const goArtifactDetail = (id) => {
  router.push(`/artifacts/${id}`);
};

const handleArtifactImageError = (event, id) => {
  if (event.target.dataset.fallbackApplied) {
    return;
  }

  event.target.dataset.fallbackApplied = 'true';
  event.target.src = `https://picsum.photos/240/160?random=${id}`;
};

onMounted(() => {
  initMap();
});

onBeforeUnmount(() => {
  map?.remove();
  map = null;
});
</script>

<style scoped>
.map-page {
  min-height: 100vh;
  background: #f5f7fb;
  padding: 32px 0 60px;
  box-sizing: border-box;
  width: 100%;
}

.header-section {
  width: 1040px;
  margin: 0 auto 24px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 40px;
}

.page-title {
  text-align: center;
  margin: 0;
  font-size: 28px;
  font-weight: 500;
  color: #000000;
}

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
  color: #203f73;
}

.panel-item .unit {
  font-size: 13px;
  font-weight: normal;
  color: #909399;
}

.collection-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
  width: 368px;
  max-height: calc(100% - 40px);
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 12px;
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.16);
  overflow: hidden;
}

.collection-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
  padding: 18px 18px 12px;
  border-bottom: 1px solid #edf0f5;
}

.panel-kicker {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #9f1239;
  font-size: 12px;
  font-weight: 700;
}

.collection-header h3 {
  margin: 8px 0 4px;
  font-size: 18px;
  line-height: 1.35;
  color: #111827;
}

.collection-header p {
  margin: 0;
  color: #6b7280;
  font-size: 12px;
  line-height: 1.5;
}

.icon-button {
  width: 32px;
  height: 32px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #ffffff;
  color: #4b5563;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.18s ease;
  flex: 0 0 auto;
}

.icon-button:hover {
  color: #9f1239;
  border-color: #fecdd3;
  background: #fff1f2;
}

.museum-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 18px 0;
  color: #4b5563;
  font-size: 13px;
}

.museum-meta span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.museum-meta a {
  color: #1d4ed8;
  text-decoration: none;
  flex: 0 0 auto;
}

.collection-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding: 14px 18px;
}

.collection-metrics div {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px 12px;
  background: #f9fafb;
}

.collection-metrics span {
  display: block;
  color: #6b7280;
  font-size: 12px;
  margin-bottom: 4px;
}

.collection-metrics strong {
  color: #203f73;
  font-size: 18px;
}

.artifact-section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 18px 10px;
  color: #111827;
  font-size: 14px;
  font-weight: 700;
}

.artifact-list,
.artifact-loading {
  padding: 0 14px 16px;
  overflow-y: auto;
}

.artifact-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.artifact-card {
  width: 100%;
  min-height: 94px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px;
  display: grid;
  grid-template-columns: 78px 1fr 18px;
  gap: 10px;
  align-items: center;
  background: #ffffff;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}

.artifact-card:hover {
  border-color: #fda4af;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  transform: translateY(-1px);
}

.artifact-card img {
  width: 78px;
  height: 78px;
  border-radius: 6px;
  object-fit: cover;
  background: #e5e7eb;
}

.artifact-info {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.artifact-info strong {
  color: #111827;
  font-size: 14px;
  line-height: 1.35;
}

.artifact-title-en,
.artifact-period {
  color: #6b7280;
  font-size: 12px;
  line-height: 1.35;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.artifact-meta {
  color: #9f1239;
  font-size: 12px;
  line-height: 1.35;
}

.artifact-arrow {
  color: #94a3b8;
}

.artifact-skeleton {
  min-height: 94px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 10px;
  display: grid;
  grid-template-columns: 78px 1fr;
  gap: 10px;
  background: #ffffff;
}

.artifact-skeleton div,
.artifact-skeleton span {
  display: block;
  border-radius: 6px;
  background: linear-gradient(90deg, #edf2f7 25%, #f8fafc 37%, #edf2f7 63%);
  background-size: 400% 100%;
  animation: loading-shimmer 1.4s ease infinite;
}

.artifact-skeleton section {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
}

.artifact-skeleton span:nth-child(1) {
  width: 85%;
  height: 16px;
}

.artifact-skeleton span:nth-child(2) {
  width: 60%;
  height: 12px;
}

.artifact-skeleton span:nth-child(3) {
  width: 72%;
  height: 12px;
}

@keyframes loading-shimmer {
  0% {
    background-position: 100% 0;
  }

  100% {
    background-position: 0 0;
  }
}

@media screen and (max-width: 1100px) {
  .header-section,
  .map-section {
    width: calc(100% - 48px);
  }
}

@media screen and (max-width: 880px) {
  .floating-panel {
    right: 20px;
    flex-wrap: wrap;
    gap: 14px 20px;
  }

  .collection-panel {
    top: auto;
    left: 12px;
    right: 12px;
    bottom: 12px;
    width: auto;
    max-height: 52%;
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

@media screen and (max-width: 560px) {
  .map-page {
    padding-top: 24px;
  }

  .header-section,
  .map-section {
    width: calc(100% - 28px);
  }

  #leaflet-map {
    height: 640px;
  }

  .floating-panel {
    top: 12px;
    left: 12px;
    right: 12px;
    padding: 12px;
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
  }

  .panel-item {
    min-width: 0;
  }

  .panel-item .label {
    font-size: 11px;
  }

  .panel-item .value {
    font-size: 18px;
  }

  .artifact-card {
    grid-template-columns: 68px 1fr 16px;
  }

  .artifact-card img {
    width: 68px;
    height: 68px;
  }
}
</style>

<style>
.museum-marker-container {
  background: transparent;
  border: none;
  overflow: visible;
}

.museum-marker {
  position: relative;
  width: 52px;
  height: 58px;
  display: flex;
  justify-content: center;
  cursor: pointer;
  transform: translate(var(--marker-offset-x, 0), var(--marker-offset-y, 0));
}

.marker-core {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #9f1239;
  color: #ffffff;
  border: 3px solid #ffffff;
  box-shadow: 0 12px 22px rgba(159, 18, 57, 0.28);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 800;
}

.marker-count {
  position: absolute;
  right: 0;
  top: -6px;
  min-width: 22px;
  height: 20px;
  padding: 0 5px;
  border-radius: 10px;
  background: #203f73;
  color: #ffffff;
  border: 2px solid #ffffff;
  font-size: 11px;
  line-height: 16px;
  text-align: center;
  font-weight: 700;
  box-shadow: 0 6px 14px rgba(32, 63, 115, 0.22);
}

.museum-marker::after {
  content: "";
  position: absolute;
  left: 22px;
  top: 38px;
  width: 10px;
  height: 10px;
  background: #9f1239;
  border-right: 3px solid #ffffff;
  border-bottom: 3px solid #ffffff;
  transform: rotate(45deg);
  box-shadow: 8px 8px 18px rgba(159, 18, 57, 0.24);
}

.museum-marker-container.is-active .marker-core {
  background: #0f766e;
  box-shadow: 0 14px 26px rgba(15, 118, 110, 0.3);
}

.museum-marker-container.is-active .museum-marker::after {
  background: #0f766e;
}

.modern-popup-style .leaflet-popup-content-wrapper {
  border-radius: 12px;
  padding: 6px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
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
  gap: 12px;
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
