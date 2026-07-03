const currentPath = window.location.pathname;

document.querySelectorAll("[data-routes]").forEach((link) => {
    const routes = link.dataset.routes.split(",");

    const isActive = routes.some((route) =>
        route === "/" ? currentPath === "/" : currentPath.startsWith(route),
    );
    if (isActive) {
        link.classList.add(
            "text-accent",
            "font-semibold",
            "border-b-2",
            "border-accent",
        );
    }
});
