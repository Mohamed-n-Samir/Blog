// Initialize state
let activeTags = [];
let quill = null;

// Initialize elements
const titleInput = document.getElementById("post-title");
const descTextarea = document.getElementById("post-desc");
const pinnedCheckbox = document.getElementById("post-pinned");
const imageInput = document.getElementById("post-image");
const imagePreview = document.getElementById("image-preview");
const imagePlaceholder = document.getElementById("image-placeholder");
const categorySelect = document.getElementById("post-category");
const btnUploadImage = document.getElementById("btn-upload-image");
const postImageFile = document.getElementById("post-image-file");

const tagInput = document.getElementById("tag-input");
const tagsWrapper = document.getElementById("tags-wrapper");

const btnSave = document.getElementById("btn-save");
const btnReset = document.getElementById("btn-reset");
const btnDelete = document.getElementById("btn-delete-current");
const searchInput = document.getElementById("search-posts");

// Extract workspace variables from DOM attributes
const editorWorkspace = document.getElementById("editor-workspace");
const currentPostId = editorWorkspace.dataset.postId ? parseInt(editorWorkspace.dataset.postId) : null;
const userId = parseInt(editorWorkspace.dataset.userId);

window.addEventListener("DOMContentLoaded", () => {
  initQuill();
  initTags();
  setupEventListeners();
  updateImagePreview(imageInput.value);
  lucide.createIcons();
});

// Setup Quill
function initQuill() {
  // Register custom Divider blot for horizontal rules (<hr>)
  const BlockEmbed = Quill.import('blots/block/embed');
  class DividerBlot extends BlockEmbed {
    static create() {
      return document.createElement('hr');
    }
  }
  DividerBlot.blotName = 'divider';
  DividerBlot.tagName = 'hr';
  Quill.register(DividerBlot);

  quill = new Quill("#editor", {
    theme: "snow",
    placeholder: "Tell your story... Use headers, bold text, blocks of code, and bullet lists.",
    modules: {
      syntax: true,
      toolbar: {
        container: [
          [{ 'header': [1, 2, false] }],
          ['bold', 'italic', 'underline', 'strike'],
          [{ 'color': ['#f97316', '#f5f5f7'] }],
          ['blockquote', 'code-block'],
          [{ 'list': 'ordered'}, { 'list': 'bullet' }],
          ['link', 'image'],
          ['divider'],
          ['clean']
        ],
        handlers: {
          'divider': function() {
            const range = this.quill.getSelection();
            if (range) {
              this.quill.insertEmbed(range.index, 'divider', true, 'user');
              this.quill.setSelection(range.index + 1);
            }
          }
        }
      }
    }
  });

  // Inject separator-horizontal icon for the divider button
  const dividerBtn = document.querySelector('.ql-divider');
  if (dividerBtn) {
    dividerBtn.title = "Insert Section Divider Line (<hr>)";
    dividerBtn.innerHTML = '<i data-lucide="separator-horizontal" class="w-4 h-4" style="stroke: currentColor;"></i>';
    if (window.lucide) {
      lucide.createIcons();
    }
  }

  // Load existing content if editing
  const existingContentEl = document.getElementById("existing-content");
  if (existingContentEl && existingContentEl.value) {
    quill.root.innerHTML = existingContentEl.value;
  }
}

// Load pre-rendered tags into state
function initTags() {
  const badges = tagsWrapper.querySelectorAll(".tag-badge");
  badges.forEach(b => {
    const name = b.dataset.tag;
    if (name) {
      activeTags.push(name);
    }
  });
}

// Setup Event Listeners
function setupEventListeners() {
  btnSave.addEventListener("click", savePost);

  btnReset.addEventListener("click", () => {
    if (confirm("Are you sure you want to revert your edits?")) {
      window.location.reload();
    }
  });

  if (btnDelete) {
    btnDelete.addEventListener("click", deletePost);
  }

  // Live image preview
  imageInput.addEventListener("input", (e) => {
    updateImagePreview(e.target.value.trim());
  });

  // Handle post featured image upload
  if (btnUploadImage && postImageFile) {
    btnUploadImage.addEventListener("click", () => {
      postImageFile.click();
    });

    postImageFile.addEventListener("change", async () => {
      const file = postImageFile.files[0];
      if (!file) return;

      // Client-side GIF validation
      if (file.type === "image/gif" || file.name.toLowerCase().endsWith(".gif")) {
        showToast("GIF images are not allowed. Please choose another format (PNG, JPG, WEBP, AVIF).", "warning");
        postImageFile.value = "";
        return;
      }

      const formData = new FormData();
      formData.append("file", file);

      try {
        btnUploadImage.disabled = true;
        btnUploadImage.innerHTML = `<i data-lucide="loader" class="w-4 h-4 animate-spin"></i> Uploading...`;
        lucide.createIcons();

        const res = await fetch("/api/upload?folder=blog_images", {
          method: "POST",
          body: formData
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || err.message || "Failed to upload image");
        }

        const data = await res.json();
        // Store only the filename in the image field
        imageInput.value = data.filename;
        // Update live preview with absolute path for immediate feedback
        updateImagePreview(data.url);
        showToast("Image uploaded successfully!");
      } catch (err) {
        showToast(err.message, "warning");
      } finally {
        btnUploadImage.disabled = false;
        btnUploadImage.innerHTML = `<i data-lucide="upload" class="w-4 h-4"></i> Upload`;
        lucide.createIcons();
        postImageFile.value = "";
      }
    });
  }

  // Client-side search filtering
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const query = e.target.value.toLowerCase().trim();
      const cards = document.querySelectorAll(".post-card");
      cards.forEach(card => {
        const titleEl = card.querySelector(".post-card-title");
        const title = titleEl ? titleEl.textContent.toLowerCase() : "";
        const descEl = card.querySelector(".post-card-desc");
        const desc = descEl ? descEl.textContent.toLowerCase() : "";
        const tags = Array.from(card.querySelectorAll(".post-card-tag")).map(t => t.textContent.toLowerCase());
        
        const match = title.includes(query) || desc.includes(query) || tags.some(t => t.includes(query));
        if (match) {
          card.classList.remove("hidden");
        } else {
          card.classList.add("hidden");
        }
      });
    });
  }

  // Tags input
  tagInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      const val = tagInput.value.trim().toUpperCase();
      if (val && !activeTags.includes(val)) {
        activeTags.push(val);
        renderTags();
      }
      tagInput.value = "";
    }
  });

  // Tags remove event delegation
  tagsWrapper.addEventListener("click", (e) => {
    const btn = e.target.closest(".remove-tag-btn");
    if (btn) {
      e.preventDefault();
      const badge = btn.closest(".tag-badge");
      const name = badge.dataset.tag;
      activeTags = activeTags.filter(t => t !== name);
      badge.remove();
    }
  });
}

function renderTags() {
  // Clear previous badges
  const badges = tagsWrapper.querySelectorAll(".tag-badge");
  badges.forEach(b => b.remove());

  // Render all active tags
  activeTags.forEach(tag => {
    const badge = document.createElement("span");
    badge.className = "tag-badge text-[10px] font-mono font-bold py-1 px-2.5 rounded flex items-center gap-1.5";
    badge.dataset.tag = tag;
    badge.innerHTML = `
      ${tag}
      <button class="hover:text-white transition remove-tag-btn">
        <i data-lucide="x" class="w-3 h-3"></i>
      </button>
    `;
    tagsWrapper.insertBefore(badge, tagInput);
  });
  lucide.createIcons();
}

function updateImagePreview(url) {
  if (url) {
    // If it's a raw filename rather than a URL or absolute path, resolve it to media path
    let src = url;
    if (url && !url.startsWith("http") && !url.startsWith("/")) {
      src = "/media/blog_images/" + url;
    }
    imagePreview.src = src;
    imagePreview.classList.remove("hidden");
    imagePlaceholder.classList.add("hidden");
    imagePreview.onerror = () => {
      imagePreview.classList.add("hidden");
      imagePlaceholder.classList.remove("hidden");
      imagePlaceholder.innerHTML = `
        <i data-lucide="image-off" class="w-6 h-6 text-red-400"></i>
        <span class="text-red-400">Failed to load image</span>
      `;
      lucide.createIcons();
    };
  } else {
    imagePreview.classList.add("hidden");
    imagePlaceholder.classList.remove("hidden");
    imagePlaceholder.innerHTML = `
      <i data-lucide="image" class="w-6 h-6 stroke-[1.5]"></i>
      <span>Live Image Preview</span>
    `;
    lucide.createIcons();
  }
}

async function savePost() {
  const title = titleInput.value.trim();
  const desc = descTextarea.value.trim();
  const content = quill.root.innerHTML.trim();
  const rawText = quill.getText().trim();

  if (!title) {
    showToast("Please enter a title.", "warning");
    titleInput.focus();
    return;
  }
  if (!desc) {
    showToast("Please enter a description.", "warning");
    descTextarea.focus();
    return;
  }
  if (rawText.length === 0) {
    showToast("Please write some content in the blog body.", "warning");
    return;
  }

  const pinned = pinnedCheckbox.checked;
  const image_file = imageInput.value.trim() || null;
  const category_id = categorySelect && categorySelect.value ? parseInt(categorySelect.value, 10) : null;

  const payload = {
    title,
    description: desc,
    content,
    pinned,
    image_file,
    category_id,
    user_id: userId,
    tags: activeTags
  };

  const url = currentPostId ? `/api/posts/${currentPostId}` : "/api/posts";
  const method = currentPostId ? "PUT" : "POST";

  try {
    const res = await fetch(url, {
      method: method,
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || err.message || "Failed to save post");
    }

    const savedPost = await res.json();
    showToast(currentPostId ? "Post updated successfully!" : "Post created successfully!");
    
    // Redirect to the edit view of the post
    setTimeout(() => {
      window.location.href = `/blog/posts/${savedPost.id}/edit`;
    }, 1000);
  } catch (err) {
    showToast(err.message, "warning");
  }
}

async function deletePost() {
  if (!currentPostId) return;
  if (!confirm("Are you sure you want to permanently delete this post? This action cannot be undone.")) return;

  try {
    const res = await fetch(`/api/posts/${currentPostId}`, {
      method: "DELETE"
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || err.message || "Failed to delete post");
    }

    showToast("Post deleted successfully!");
    setTimeout(() => {
      window.location.href = `/users/${userId}/posts/new`;
    }, 1000);
  } catch (err) {
    showToast(err.message, "warning");
  }
}

function showToast(message, type = "success") {
  const toast = document.getElementById("toast");
  const toastMsg = document.getElementById("toast-message");
  const iconContainer = document.getElementById("toast-icon-container");
  
  toastMsg.textContent = message;
  
  if (iconContainer) {
    const iconName = type === "success" ? "check-circle" : "alert-circle";
    iconContainer.innerHTML = `<i data-lucide="${iconName}" class="w-4 h-4"></i>`;
  }
  
  if (type === "success") {
    toast.className = "fixed bottom-6 right-6 z-50 py-3 px-5 bg-emerald-500/10 border border-emerald-500 text-emerald-400 rounded-xl text-xs font-semibold flex items-center gap-2 shadow-xl shadow-emerald-500/10 transition-all duration-300 transform translate-y-0 opacity-100";
  } else {
    toast.className = "fixed bottom-6 right-6 z-50 py-3 px-5 bg-amber-500/10 border border-amber-500 text-amber-400 rounded-xl text-xs font-semibold flex items-center gap-2 shadow-xl shadow-amber-500/10 transition-all duration-300 transform translate-y-0 opacity-100";
  }

  lucide.createIcons();

  setTimeout(() => {
    toast.className = "fixed bottom-6 right-6 z-50 py-3 px-5 bg-accent-2/15 border border-accent-2 text-accent-2 rounded-xl text-xs font-semibold flex items-center gap-2 shadow-xl shadow-accent-2/10 transition-all duration-300 transform translate-y-12 opacity-0 pointer-events-none";
  }, 3000);
}
