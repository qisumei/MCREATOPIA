// 导航栏隐藏/显示逻辑
let lastScroll = 0;
const navbar = document.getElementById('navbar');

window.addEventListener('scroll', () => {
  const currentScroll = window.pageYOffset;
  if (currentScroll > lastScroll) {
    navbar.style.top = '-80px'; // 向下滚动隐藏
  } else {
    navbar.style.top = '0'; // 向上滚动显示
  }
  lastScroll = currentScroll;
});

// 滑入动画
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
});

document.querySelectorAll('.fade-in-left, .fade-in-right').forEach(el => {
  observer.observe(el);
});
