// ==UserScript==
// @name         Proxy (moo)
// @match        *://moomoo.io/*
// @grant        none
// ==/UserScript==

(function () {
    // Save the original WebSocket in a variable
    const OriginalWebSocket = window.WebSocket;

    // Create a custom WebSocket class that extends the original WebSocket
    class OasisSocket extends OriginalWebSocket {
        constructor() {
            // Connect to the local proxy server
            super("ws://127.0.0.1:3000");
        }
    }

    // Replace the global WebSocket with the custom OasisSocket
    window.WebSocket = OasisSocket;
})();
