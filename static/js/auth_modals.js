document.addEventListener("DOMContentLoaded", () => {
  const loginModal = document.getElementById("login-modal");
  const registerModal = document.getElementById("register-modal");
  
  const loginBtn = document.getElementById("nav-login-btn");
  const registerBtn = document.getElementById("nav-register-btn");
  
  const toRegisterBtn = document.getElementById("to-register-btn");
  const toLoginBtn = document.getElementById("to-login-btn");
  
  const closeBtns = document.querySelectorAll(".close-modal-btn");

  // Helper to open a modal
  function openModal(modal) {
    if (!modal) return;
    modal.classList.remove("hidden");
    // Force reflow
    modal.offsetHeight;
    modal.classList.add("opacity-100");
    const panel = modal.querySelector(".panel");
    if (panel) {
      panel.classList.remove("scale-95");
      panel.classList.add("scale-100");
    }
    document.body.style.overflow = "hidden"; // Prevent background scrolling
  }

  // Helper to close a modal
  function closeModal(modal) {
    if (!modal) return;
    modal.classList.remove("opacity-100");
    const panel = modal.querySelector(".panel");
    if (panel) {
      panel.classList.remove("scale-100");
      panel.classList.add("scale-95");
    }
    
    // Wait for transition to complete
    setTimeout(() => {
      modal.classList.add("hidden");
      // Restore background scrolling only if no other modals are open
      if ((!loginModal || loginModal.classList.contains("hidden")) && 
          (!registerModal || registerModal.classList.contains("hidden"))) {
        document.body.style.overflow = "";
      }
    }, 300);
  }

  // Event Listeners for Opening
  if (loginBtn) {
    loginBtn.addEventListener("click", (e) => {
      e.preventDefault();
      openModal(loginModal);
    });
  }

  if (registerBtn) {
    registerBtn.addEventListener("click", (e) => {
      e.preventDefault();
      openModal(registerModal);
    });
  }

  // Event Listeners for Switching
  if (toRegisterBtn) {
    toRegisterBtn.addEventListener("click", () => {
      closeModal(loginModal);
      setTimeout(() => {
        openModal(registerModal);
      }, 150);
    });
  }

  if (toLoginBtn) {
    toLoginBtn.addEventListener("click", () => {
      closeModal(registerModal);
      setTimeout(() => {
        openModal(loginModal);
      }, 150);
    });
  }

  // Close buttons inside modals
  closeBtns.forEach(btn => {
    btn.addEventListener("click", (e) => {
      const modal = e.target.closest(".fixed");
      if (modal) {
        closeModal(modal);
      }
    });
  });

  // Close when clicking outside the modal content panel (backdrop click)
  window.addEventListener("click", (e) => {
    if (e.target === loginModal) {
      closeModal(loginModal);
    }
    if (e.target === registerModal) {
      closeModal(registerModal);
    }
  });

  // Close when hitting escape key
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (loginModal && !loginModal.classList.contains("hidden")) {
        closeModal(loginModal);
      }
      if (registerModal && !registerModal.classList.contains("hidden")) {
        closeModal(registerModal);
      }
    }
  });

  // Handle Login Form Submission
  const loginForm = document.getElementById("login-form");
  const loginErrorContainer = document.getElementById("login-error-container");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const usernameInput = document.getElementById("login-email");
      const passwordInput = document.getElementById("login-password");
      
      const username = usernameInput ? usernameInput.value.trim() : "";
      const password = passwordInput ? passwordInput.value : "";
      
      if (!username || !password) {
        showError(loginErrorContainer, "Please fill in all fields.");
        return;
      }
      
      try {
        const res = await fetch("/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ username, password })
        });
        
        const data = await res.json();
        if (res.ok && data.success) {
          window.location.reload();
        } else {
          showError(loginErrorContainer, data.message || "Failed to login.");
        }
      } catch (err) {
        showError(loginErrorContainer, "Network error occurred.");
      }
    });
  }

  // Handle Register Form Submission
  const registerForm = document.getElementById("register-form");
  const registerErrorContainer = document.getElementById("register-error-container");
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const firstNameInput = document.getElementById("register-first-name");
      const lastNameInput = document.getElementById("register-last-name");
      const usernameInput = document.getElementById("register-username");
      const emailInput = document.getElementById("register-email");
      const passwordInput = document.getElementById("register-password");
      const confirmPasswordInput = document.getElementById("register-confirm-password");
      
      const first_name = firstNameInput ? firstNameInput.value.trim() : "";
      const last_name = lastNameInput ? lastNameInput.value.trim() : "";
      const username = usernameInput ? usernameInput.value.trim() : "";
      const email = emailInput ? emailInput.value.trim() : "";
      const password = passwordInput ? passwordInput.value : "";
      const confirmPassword = confirmPasswordInput ? confirmPasswordInput.value : "";
      
      if (!username || !email || !password || !confirmPassword) {
        showError(registerErrorContainer, "Please fill in all fields.");
        return;
      }
      
      if (password !== confirmPassword) {
        showError(registerErrorContainer, "Passwords do not match.");
        return;
      }
      
      try {
        const res = await fetch("/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ username, email, password, first_name, last_name })
        });
        
        const data = await res.json();
        if (res.ok && data.success) {
          window.location.reload();
        } else {
          showError(registerErrorContainer, data.message || "Failed to register.");
        }
      } catch (err) {
        showError(registerErrorContainer, "Network error occurred.");
      }
    });
  }

  function showError(container, msg) {
    if (!container) return;
    container.textContent = msg;
    container.classList.remove("hidden");
  }
});
