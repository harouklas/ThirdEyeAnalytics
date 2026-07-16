(function () {
    "use strict";

    const storageKey = "thirdeye-theme";
    const root = document.documentElement;

    // Read only the two themes used by the site and ignore any changed value.
    function readSavedTheme() {
        try {
            const savedTheme = window.localStorage.getItem(storageKey);
            return savedTheme === "dark" || savedTheme === "light" ? savedTheme : "light";
        } catch (error) {
            return "light";
        }
    }

    // localStorage keeps the choice when the user moves to another page.
    function saveTheme(theme) {
        try {
            window.localStorage.setItem(storageKey, theme);
        } catch (error) {
            // The selected theme still works for this page when storage is unavailable.
        }
    }

    // Keep the visible button and its screen-reader text on the same state.
    function updateToggle(theme) {
        const toggle = document.getElementById("theme-toggle");
        if (!toggle) {
            return;
        }

        const isDark = theme === "dark";
        const actionLabel = isDark ? "Switch to light mode" : "Switch to dark mode";
        toggle.setAttribute("aria-pressed", String(isDark));
        toggle.setAttribute("aria-label", actionLabel);
        toggle.setAttribute("title", actionLabel);
    }

    // data-theme lets the CSS variables switch the colours for the whole page.
    function applyTheme(theme) {
        root.dataset.theme = theme;
        updateToggle(theme);
    }

    // Apply this before DOMContentLoaded to prevent the wrong theme flashing.
    const initialTheme = readSavedTheme();
    applyTheme(initialTheme);

    document.addEventListener("DOMContentLoaded", function () {
        updateToggle(initialTheme);

        const toggle = document.getElementById("theme-toggle");
        if (!toggle) {
            return;
        }

        // Each click swaps the current value and then remembers it.
        toggle.addEventListener("click", function () {
            const nextTheme = root.dataset.theme === "dark" ? "light" : "dark";
            applyTheme(nextTheme);
            saveTheme(nextTheme);
        });
    });
}());
