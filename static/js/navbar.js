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

// Dropdown toggle logic
document.addEventListener("DOMContentLoaded", () => {
    const menuButton = document.getElementById("user-menu-button");
    const menuDropdown = document.getElementById("user-menu-dropdown");

    if (menuButton && menuDropdown) {
        menuButton.addEventListener("click", (e) => {
            e.stopPropagation();
            const expanded = menuButton.getAttribute("aria-expanded") === "true";
            menuButton.setAttribute("aria-expanded", !expanded);
            
            if (expanded) {
                menuDropdown.classList.add("opacity-0", "scale-95", "pointer-events-none");
            } else {
                menuDropdown.classList.remove("opacity-0", "scale-95", "pointer-events-none");
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener("click", () => {
            menuButton.setAttribute("aria-expanded", "false");
            menuDropdown.classList.add("opacity-0", "scale-95", "pointer-events-none");
        });
    }
});
