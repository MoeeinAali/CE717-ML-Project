## How to use:

```js
(function() {
    var script = document.createElement('script');
    script.src = "http://localhost:8000/static/widget.js"; 
    script.onload = function() {
        console.log("Chatbot Widget Loaded Successfully!");
    };
    script.onerror = function() {
        console.error("Failed to load the widget. Check if server is running.");
    };
    document.head.appendChild(script);
})();
```