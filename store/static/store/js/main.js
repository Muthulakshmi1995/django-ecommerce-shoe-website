document.addEventListener("DOMContentLoaded", () => {
  // Homepage hero carousel
  const slides = [...document.querySelectorAll(".hero-slide")];
  const dots = [...document.querySelectorAll(".hero-dots .dot")];
  if (slides.length > 1) {
    let current = 0;
    const show = (index) => {
      current = index;
      slides.forEach((slide, i) => slide.classList.toggle("active", i === current));
      dots.forEach((dot, i) => dot.classList.toggle("active", i === current));
    };
    dots.forEach((dot, i) => dot.addEventListener("click", () => show(i)));
    window.setInterval(() => show((current + 1) % slides.length), 5500);
  }
  // Product gallery main image interaction
  const galleryButtons = [...document.querySelectorAll(".gallery-image")];
  if (galleryButtons.length > 1) {
    galleryButtons.forEach((button) => button.addEventListener("click", () => {
      galleryButtons.forEach((b) => b.classList.remove("selected"));
      button.classList.add("selected");
      const main = button.querySelector("img");
      if (main) {
        galleryButtons.forEach((b) => b.querySelector("img")?.classList.remove("zoomed"));
        main.classList.add("zoomed");
      }
    }));
  }
  // Quantity stepper
  document.querySelectorAll("[data-qty]").forEach((button) => button.addEventListener("click", () => {
    const input = document.getElementById("quantity");
    if (!input) return;
    const delta = Number(button.dataset.qty || 0);
    input.value = Math.max(1, Math.min(20, Number(input.value || 1) + delta));
  }));
  document.querySelectorAll('input[name="colour"]').forEach((input) => input.addEventListener("change", () => {
    const label = document.getElementById("chosen-colour");
    if (label) label.textContent = input.value;
  }));
});
