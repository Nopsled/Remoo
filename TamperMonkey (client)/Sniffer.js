// ==UserScript==
// @name         Sniffer
// @match        *://moomoo.io/*
// @grant        none
// @require https://greasyfork.org/scripts/423602-msgpack/code/msgpack.js?version=1005014
// ==/UserScript==

function uint8ArrayToHex(arr) {
    return Array.prototype.map.call(arr, function(n) {
        return (n < 16 ? '0' : '') + n.toString(16);
    }).join('\\x');
}


(function() {


    let originalWebSocket = window.WebSocket;
    window.WebSocket = function(url) {
        let ws = new originalWebSocket(url);

        ws.addEventListener("open", event => {
            console.log("WebSocket connection opened:", event);
        });
        ws.addEventListener("close", event => {
            console.log("WebSocket connection closed:", event);
        });
        ws.addEventListener("message", event => {

            var rawData = new Uint8Array(event.data);
            var hexData = uint8ArrayToHex(rawData)
            var decodedData = msgpack.decode(rawData);
            if (decodedData[0] != "pp" && decodedData[0] != "33" && decodedData[0] != "a")
                console.log("Recieved: ", decodedData);

        });

        ws.send = function(data) {

            var rawData = new Uint8Array(data);
            var hexData = uint8ArrayToHex(rawData)
            var decodedData = msgpack.decode(data);
            var header = decodedData[0].toString();

            //console.log(header.toString())
            if (header != "pp" && header != "2")
                console.log("Sent: ", decodedData);

            // PACKET INTERCEPTION

            //if(header == "sp") {
            //    var newData = ["sp", [{"name": "aaaaasas", "moofoll": null, "skin": 1}]]
            //    data = msgpack.encode(newData);
            //    console.log("New data: ", msgpack.decode(data))
            //    console.log("PACKET INTERCEPTED!!!");
            //}


            originalWebSocket.prototype.send.call(this, data);

        };

        return ws;
    };
})();
