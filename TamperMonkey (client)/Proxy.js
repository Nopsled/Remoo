// ==UserScript==
// @name         Proxy (moo)
// @match        *://moomoo.io/*
// @grant        none
// ==/UserScript==

(function (){
    let ws = window.WebSocket;
    class OasisSocket extends ws {
        constructor(){
            super("ws://127.0.0.1:3000");
        }
    }
    window.WebSocket = OasisSocket;
})();