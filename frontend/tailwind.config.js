/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                'civ-dark': '#0a0a0a',
                'civ-panel': '#111111',
                'civ-accent': '#333333',
            },
        },
    },
    plugins: [],
};
