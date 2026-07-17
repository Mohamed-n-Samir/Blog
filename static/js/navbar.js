const currentPath = window.location.pathname;

function initNavbar() {
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
            if (menuButton && menuDropdown) {
                menuButton.setAttribute("aria-expanded", "false");
                menuDropdown.classList.add("opacity-0", "scale-95", "pointer-events-none");
            }
        });
    }

    // Mobile menu toggle logic
    const mobileMenuToggle = document.getElementById("mobile-menu-toggle");
    const mobileMenu = document.getElementById("mobile-menu");
    const menuIconOpen = document.getElementById("menu-icon-open");
    const menuIconClose = document.getElementById("menu-icon-close");

    console.log("[NAVBAR JS] initNavbar executed.");
    console.log("[NAVBAR JS] mobileMenuToggle:", mobileMenuToggle);
    console.log("[NAVBAR JS] mobileMenu:", mobileMenu);
    console.log("[NAVBAR JS] menuIconOpen:", menuIconOpen);
    console.log("[NAVBAR JS] menuIconClose:", menuIconClose);

    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener("click", (e) => {
            console.log("[NAVBAR JS] Toggle clicked!");
            e.stopPropagation();
            const isClosed = mobileMenu.classList.contains("pointer-events-none");
            console.log("[NAVBAR JS] Current closed state:", isClosed);
            if (isClosed) {
                // Open the menu smoothly
                mobileMenu.classList.remove("max-h-0", "opacity-0", "pointer-events-none", "py-0");
                mobileMenu.classList.add("max-h-60", "opacity-100", "pointer-events-auto", "py-4");
                if (menuIconOpen) {
                    menuIconOpen.classList.add("hidden");
                    menuIconOpen.classList.remove("block");
                }
                if (menuIconClose) {
                    menuIconClose.classList.remove("hidden");
                    menuIconClose.classList.add("block");
                }
            } else {
                // Close the menu smoothly
                mobileMenu.classList.remove("max-h-60", "opacity-100", "pointer-events-auto", "py-4");
                mobileMenu.classList.add("max-h-0", "opacity-0", "pointer-events-none", "py-0");
                if (menuIconOpen) {
                    menuIconOpen.classList.remove("hidden");
                    menuIconOpen.classList.add("block");
                }
                if (menuIconClose) {
                    menuIconClose.classList.add("hidden");
                    menuIconClose.classList.remove("block");
                }
            }
        });

        // Close mobile menu when clicking outside
        document.addEventListener("click", (e) => {
            if (!mobileMenu.contains(e.target) && !mobileMenuToggle.contains(e.target)) {
                const isOpen = !mobileMenu.classList.contains("pointer-events-none");
                if (isOpen) {
                    mobileMenu.classList.remove("max-h-60", "opacity-100", "pointer-events-auto", "py-4");
                    mobileMenu.classList.add("max-h-0", "opacity-0", "pointer-events-none", "py-0");
                    if (menuIconOpen) {
                        menuIconOpen.classList.remove("hidden");
                        menuIconOpen.classList.add("block");
                    }
                    if (menuIconClose) {
                        menuIconClose.classList.add("hidden");
                        menuIconClose.classList.remove("block");
                    }
                }
            }
        });
    }
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initNavbar);
} else {
    initNavbar();
}
