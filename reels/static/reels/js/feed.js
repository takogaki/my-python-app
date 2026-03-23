const videos = document.querySelectorAll('.video');

let currentVideo = null;

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    const video = entry.target;

    if (entry.isIntersecting) {

      if (currentVideo && currentVideo !== video) {
        currentVideo.pause();
      }

      video.play();
      currentVideo = video;

    } else {
      video.pause();
    }
  });
}, { threshold: 0.8 });

videos.forEach(video => {
  observer.observe(video);

  video.addEventListener('click', () => {
    video.muted = !video.muted;
  });
});


// 🔥 ここに追加
window.addEventListener('load', () => {
  const firstVideo = document.querySelector('.video');
  if (firstVideo) {
    firstVideo.play();
    currentVideo = firstVideo; // ← これも重要（状態同期）
  }
});