export const THEME_KEY = "ohw.theme";

// Runs in <head> before the page paints, so a light-mode reader never sees a dark flash.
// Saved choice wins; otherwise follow the device setting, and keep following it if it
// changes (until the reader picks a theme with the switch).
export const themeScript = `(function(){
var d=document.documentElement,k=${JSON.stringify(THEME_KEY)},m=window.matchMedia("(prefers-color-scheme: light)");
function saved(){try{return localStorage.getItem(k)}catch(e){return null}}
d.dataset.theme=saved()||(m.matches?"light":"dark");
if(m.addEventListener)m.addEventListener("change",function(e){if(!saved())d.dataset.theme=e.matches?"light":"dark"});
})();`;
