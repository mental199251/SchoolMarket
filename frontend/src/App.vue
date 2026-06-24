<script>
export default {
  onLaunch: function () {
    console.log('App Launch')
  },
  onShow: function () {
    console.log('App Show')
  },
  onHide: function () {
    console.log('App Hide')
  },
}
</script>

<style>
page {
  min-height: 100%;
  background:
    radial-gradient(circle at 10% 8%, rgba(255, 215, 170, 0.72) 0, rgba(255, 215, 170, 0) 260rpx),
    radial-gradient(circle at 88% 2%, rgba(178, 230, 255, 0.78) 0, rgba(178, 230, 255, 0) 300rpx),
    linear-gradient(145deg, #fff8ec 0%, #f0fbf5 46%, #eef6ff 100%);
  color: #20352f;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Microsoft YaHei", sans-serif;
}

button::after {
  border: 0;
}

button,
input,
textarea,
picker,
.select,
.product-card,
.trade-card,
.message-card,
.announcement-card,
.user-card,
.log-card,
.chart-card,
.metric-card,
.status-card,
.profile-card,
.form-card,
.form-panel {
  box-sizing: border-box;
}

.page {
  width: 100% !important;
  max-width: 980px !important;
  min-height: 100vh !important;
  margin: 0 auto !important;
  padding: 44rpx 28rpx 92rpx !important;
  color: #20352f !important;
  background:
    radial-gradient(circle at 12% 4%, rgba(255, 219, 190, 0.76) 0, rgba(255, 219, 190, 0) 250rpx),
    radial-gradient(circle at 90% 12%, rgba(185, 225, 255, 0.78) 0, rgba(185, 225, 255, 0) 300rpx),
    radial-gradient(circle at 36% 92%, rgba(196, 241, 212, 0.76) 0, rgba(196, 241, 212, 0) 280rpx),
    linear-gradient(160deg, #fffaf1 0%, #f1fbf6 52%, #eef7ff 100%) !important;
  background-size: 140% 140% !important;
  animation: v2-page-breathe 9s ease-in-out infinite alternate;
}

.header,
.hero {
  position: relative !important;
  overflow: hidden !important;
  margin-bottom: 30rpx !important;
  padding: 34rpx !important;
  border: 2rpx solid rgba(255, 255, 255, 0.78) !important;
  border-radius: 42rpx !important;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(240, 255, 248, 0.74)),
    radial-gradient(circle at 88% 8%, rgba(118, 210, 188, 0.25), rgba(118, 210, 188, 0)) !important;
  box-shadow: 0 28rpx 64rpx rgba(65, 124, 111, 0.16), inset 0 -10rpx 22rpx rgba(255, 255, 255, 0.8) !important;
  animation: v2-pop-in 360ms cubic-bezier(0.2, 0.9, 0.2, 1) both;
}

.header::before,
.hero::before {
  content: "";
  position: absolute;
  right: -44rpx;
  top: -48rpx;
  width: 170rpx;
  height: 170rpx;
  border-radius: 999rpx;
  background: rgba(255, 195, 143, 0.42);
  box-shadow: -84rpx 104rpx 0 rgba(164, 225, 208, 0.36), -190rpx 42rpx 0 rgba(184, 222, 255, 0.34);
  animation: v2-float 6s ease-in-out infinite alternate;
}

.eyebrow {
  position: relative !important;
  display: inline-flex !important;
  align-items: center !important;
  align-self: flex-start !important;
  margin-bottom: 12rpx !important;
  padding: 8rpx 18rpx !important;
  border: 1rpx solid rgba(24, 165, 138, 0.18) !important;
  border-radius: 999rpx !important;
  background: rgba(255, 255, 255, 0.76) !important;
  color: #147a69 !important;
  font-size: 22rpx !important;
  font-weight: 800 !important;
  letter-spacing: 0 !important;
  line-height: 1.35 !important;
  box-shadow: 0 12rpx 24rpx rgba(52, 130, 111, 0.1) !important;
}

.title {
  position: relative !important;
  display: block !important;
  color: #183b34 !important;
  font-size: 52rpx !important;
  font-weight: 900 !important;
  line-height: 1.12 !important;
  letter-spacing: 0 !important;
}

.subtitle {
  position: relative !important;
  display: block !important;
  margin-top: 14rpx !important;
  color: #60766f !important;
  font-size: 27rpx !important;
  line-height: 1.58 !important;
}

.form-card,
.form-panel,
.status-card,
.admin-panel,
.profile-card,
.info-list,
.status-panel,
.product-card,
.trade-card,
.message-card,
.announcement-card,
.user-card,
.log-card,
.chart-card,
.metric-card,
.section,
.seller-row {
  position: relative !important;
  overflow: hidden !important;
  margin-bottom: 22rpx !important;
  padding: 26rpx !important;
  border: 2rpx solid rgba(255, 255, 255, 0.8) !important;
  border-radius: 34rpx !important;
  background: rgba(255, 255, 255, 0.84) !important;
  box-shadow:
    0 22rpx 52rpx rgba(77, 130, 120, 0.13),
    inset 0 2rpx 0 rgba(255, 255, 255, 0.9),
    inset 0 -10rpx 24rpx rgba(227, 246, 239, 0.72) !important;
  animation: v2-card-rise 320ms cubic-bezier(0.2, 0.9, 0.2, 1) both;
}

.product-card,
.trade-card,
.message-card,
.announcement-card,
.user-card,
.log-card,
.chart-card {
  transform-origin: center;
  transition: transform 180ms ease, box-shadow 180ms ease, background 180ms ease;
}

.product-card:active,
.trade-card:active,
.message-card:active,
.announcement-card:active,
.user-card:active,
.chart-card:active,
button:active,
.action-button:active,
.section-link:active {
  transform: scale(0.985);
}

.input,
.search-input,
.textarea,
.select {
  min-height: 88rpx !important;
  border: 2rpx solid rgba(34, 165, 137, 0.16) !important;
  border-radius: 26rpx !important;
  background: rgba(255, 255, 255, 0.88) !important;
  color: #20352f !important;
  font-size: 28rpx !important;
  line-height: 1.45 !important;
  box-shadow: inset 0 6rpx 18rpx rgba(138, 177, 168, 0.12), 0 10rpx 24rpx rgba(68, 126, 112, 0.06) !important;
  transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease;
}

.input,
.search-input {
  padding: 0 24rpx !important;
}

.textarea {
  min-height: 240rpx !important;
  padding: 24rpx !important;
}

.select {
  display: flex !important;
  align-items: center !important;
  height: auto !important;
  padding: 0 24rpx !important;
  color: #4e665e !important;
  font-weight: 700 !important;
}

.label {
  display: block !important;
  margin: 26rpx 0 12rpx !important;
  color: #2b5d52 !important;
  font-size: 25rpx !important;
  font-weight: 900 !important;
}

.label.inline {
  margin: 0 !important;
}

.primary-button,
.secondary-button,
.ghost-button,
.danger-button,
.search-button,
.small-button,
.apply-button,
.remove-button,
.nav-button,
.publish-button,
.icon-button,
.quick-button,
.admin-button,
.action-button,
.load-more {
  min-height: 76rpx !important;
  padding: 0 28rpx !important;
  border: 0 !important;
  border-radius: 999rpx !important;
  font-size: 26rpx !important;
  font-weight: 900 !important;
  line-height: 76rpx !important;
  text-align: center !important;
  letter-spacing: 0 !important;
  box-shadow: 0 14rpx 28rpx rgba(38, 117, 100, 0.15), inset 0 -8rpx 16rpx rgba(16, 85, 72, 0.08) !important;
  transition: transform 180ms ease, opacity 180ms ease, box-shadow 180ms ease !important;
}

.primary-button,
.quick-button.primary,
.action-button.primary,
.search-button,
.publish-button {
  background: linear-gradient(135deg, #18a58a 0%, #64cfae 54%, #8bdff0 100%) !important;
  color: #08342d !important;
}

.secondary-button,
.quick-button,
.admin-button,
.nav-button,
.icon-button,
.small-button,
.apply-button,
.load-more,
.action-button {
  background: linear-gradient(135deg, #ffffff 0%, #e8fff6 100%) !important;
  color: #18594e !important;
}

.ghost-button,
.icon-button.ghost {
  background: rgba(255, 255, 255, 0.58) !important;
  color: #52746b !important;
  box-shadow: inset 0 0 0 2rpx rgba(31, 148, 127, 0.13) !important;
}

.danger-button,
.action-button.danger,
.remove-button {
  background: linear-gradient(135deg, #fff2f4 0%, #ffd6de 100%) !important;
  color: #ab2742 !important;
}

button[disabled],
.disabled,
.action-button.disabled {
  opacity: 0.52 !important;
  transform: none !important;
}

.quick-grid,
.admin-grid,
.metric-grid,
.filter-grid,
.form-actions,
.actions,
.card-actions,
.header-actions {
  gap: 18rpx !important;
}

.quick-grid,
.admin-grid,
.metric-grid {
  display: grid !important;
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  margin-bottom: 26rpx !important;
}

.filter-grid {
  display: grid !important;
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  margin-bottom: 20rpx !important;
}

.search-row {
  display: flex !important;
  align-items: center !important;
  gap: 16rpx !important;
  margin-bottom: 20rpx !important;
}

.search-input {
  flex: 1 !important;
  min-width: 0 !important;
}

.empty {
  margin: 24rpx 0 !important;
  padding: 70rpx 28rpx !important;
  border: 2rpx dashed rgba(58, 154, 134, 0.24) !important;
  border-radius: 34rpx !important;
  background: rgba(255, 255, 255, 0.64) !important;
  color: #668078 !important;
  font-size: 28rpx !important;
  line-height: 1.5 !important;
  text-align: center !important;
}

.empty.compact {
  padding: 34rpx 24rpx !important;
}

.section-heading {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 16rpx !important;
  margin: 34rpx 0 18rpx !important;
}

.section-title,
.panel-title {
  color: #183b34 !important;
  font-size: 33rpx !important;
  font-weight: 900 !important;
  line-height: 1.25 !important;
}

.section-link {
  min-height: 56rpx !important;
  padding: 0 20rpx !important;
  border-radius: 999rpx !important;
  background: rgba(255, 255, 255, 0.76) !important;
  color: #147a69 !important;
  font-size: 24rpx !important;
  font-weight: 900 !important;
  line-height: 56rpx !important;
  box-shadow: 0 10rpx 22rpx rgba(54, 122, 108, 0.1) !important;
}

.product-image,
.trade-image,
.preview,
.hero-image,
.image-placeholder,
.hero-placeholder {
  border: 4rpx solid rgba(255, 255, 255, 0.78) !important;
  border-radius: 30rpx !important;
  background:
    radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0)),
    linear-gradient(135deg, #d8fff0 0%, #dff1ff 100%) !important;
  color: #16816f !important;
  box-shadow: inset 0 -12rpx 24rpx rgba(31, 154, 126, 0.12), 0 18rpx 34rpx rgba(68, 126, 112, 0.12) !important;
}

.product-title,
.trade-title,
.announcement-title,
.message-title,
.log-title,
.chart-title,
.name,
.seller-name {
  color: #173b34 !important;
  font-size: 30rpx !important;
  font-weight: 900 !important;
  line-height: 1.36 !important;
}

.product-meta,
.trade-meta,
.meta,
.seller,
.target-id,
.details,
.announcement-content,
.message-content,
.description,
.seller-campus,
.info-label,
.metric-label,
.chart-meta,
.status-label {
  color: #60766f !important;
  font-size: 24rpx !important;
  line-height: 1.55 !important;
}

.price,
.metric-value,
.chart-number {
  color: #c95f36 !important;
  font-weight: 950 !important;
  letter-spacing: 0 !important;
}

.status,
.tag,
.target,
.read-dot {
  display: inline-flex !important;
  align-items: center !important;
  align-self: flex-start !important;
  min-height: 42rpx !important;
  padding: 0 16rpx !important;
  border-radius: 999rpx !important;
  background: #fff1dc !important;
  color: #8b4e13 !important;
  font-size: 22rpx !important;
  font-weight: 900 !important;
  line-height: 42rpx !important;
}

.status-available,
.status-active,
.status-published,
.status-completed,
.status-confirmed {
  background: #ddf8ed !important;
  color: #126957 !important;
}

.status-off_shelf,
.status-cancelled,
.status-disabled,
.status-draft {
  background: #eef2f1 !important;
  color: #5f706b !important;
}

.status-sold,
.status-pending {
  background: #fff0d6 !important;
  color: #955c14 !important;
}

.avatar {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  border: 4rpx solid rgba(255, 255, 255, 0.82) !important;
  border-radius: 999rpx !important;
  background: linear-gradient(135deg, #dbfff2 0%, #dceeff 100%) !important;
  color: #12725f !important;
  font-weight: 950 !important;
  box-shadow: 0 18rpx 34rpx rgba(65, 124, 111, 0.13), inset 0 -10rpx 22rpx rgba(79, 192, 164, 0.13) !important;
}

.bar-track {
  overflow: hidden !important;
  border-radius: 999rpx !important;
  background: rgba(216, 234, 229, 0.72) !important;
}

.bar-fill {
  border-radius: 999rpx !important;
  background: linear-gradient(90deg, #18a58a, #8bdff0, #ffd2a6) !important;
  animation: v2-bar-grow 520ms ease both;
}

.suggestion-list,
.image-grid {
  gap: 14rpx !important;
}

.suggestion-item {
  border: 2rpx solid rgba(255, 255, 255, 0.8) !important;
  border-radius: 28rpx !important;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(241, 255, 248, 0.82)) !important;
  box-shadow: 0 16rpx 34rpx rgba(79, 132, 121, 0.12) !important;
}

.suggestion-text {
  color: #31554c !important;
  line-height: 1.5 !important;
}

.read-dot.active {
  width: 20rpx !important;
  height: 20rpx !important;
  min-height: 20rpx !important;
  padding: 0 !important;
  background: #18a58a !important;
  box-shadow: 0 0 0 8rpx rgba(24, 165, 138, 0.14) !important;
}

.image-swiper,
.hero-placeholder {
  border-radius: 42rpx !important;
}

.hero-placeholder {
  min-height: 420rpx !important;
}

@media screen and (min-width: 768px) {
  .page {
    padding: 56rpx 44rpx 110rpx !important;
  }

  .quick-grid,
  .admin-grid,
  .metric-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
  }

  .product-card,
  .trade-card,
  .message-card,
  .announcement-card,
  .user-card,
  .log-card,
  .chart-card {
    padding: 30rpx !important;
  }
}

@media (prefers-reduced-motion: reduce) {
  .page,
  .header,
  .hero,
  .product-card,
  .trade-card,
  .message-card,
  .announcement-card,
  .user-card,
  .log-card,
  .chart-card,
  .bar-fill {
    animation: none !important;
    transition: none !important;
  }
}

@keyframes v2-page-breathe {
  from {
    background-position: 0% 0%;
  }
  to {
    background-position: 100% 70%;
  }
}

@keyframes v2-float {
  from {
    transform: translate3d(0, 0, 0) scale(1);
  }
  to {
    transform: translate3d(-18rpx, 20rpx, 0) scale(1.04);
  }
}

@keyframes v2-pop-in {
  from {
    opacity: 0;
    transform: translateY(20rpx) scale(0.985);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes v2-card-rise {
  from {
    opacity: 0;
    transform: translateY(18rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes v2-bar-grow {
  from {
    transform: scaleX(0);
    transform-origin: left center;
  }
  to {
    transform: scaleX(1);
    transform-origin: left center;
  }
}
</style>
