// Bump this string on every deploy — it forces old caches out.
var CACHE_NAME = "kosh-shell-v3";
var SHELL_FILES = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icon.svg",
  "./icon-maskable.svg"
];

self.addEventListener("install", function(event){
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache){
      return cache.addAll(SHELL_FILES);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", function(event){
  event.waitUntil(
    caches.keys().then(function(keys){
      return Promise.all(
        keys.filter(function(key){ return key !== CACHE_NAME && key.indexOf("kosh-dict") !== 0; })
            .map(function(key){ return caches.delete(key); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", function(event){
  var url = event.request.url;
  var req = event.request;

  // Online dictionary lookups: straight to the network, never cached.
  if(url.indexOf("api.dictionaryapi.dev") !== -1 ||
     url.indexOf("wiktionary.org") !== -1 ||
     url.indexOf("datamuse.com") !== -1){
    return;
  }
  // Offline dictionary shards: the app manages these in its own cache.
  if(url.indexOf("/dict/") !== -1){ return; }
  if(req.method !== "GET"){ return; }

  // HTML and JS: NETWORK FIRST. Cache-first here was the bug that pinned the app
  // to whatever version was installed first — new deploys were never picked up.
  var isShell = req.mode === "navigate" ||
                url.indexOf(".html") !== -1 ||
                url.indexOf(".js") !== -1 ||
                url.indexOf(".json") !== -1;

  if(isShell){
    event.respondWith(
      fetch(req).then(function(response){
        if(response && response.status === 200){
          var copy = response.clone();
          caches.open(CACHE_NAME).then(function(c){ c.put(req, copy); });
        }
        return response;
      }).catch(function(){
        // Offline: fall back to the last good copy.
        return caches.match(req).then(function(hit){
          return hit || caches.match("./index.html");
        });
      })
    );
    return;
  }

  // Everything else (icons): cache first is fine.
  event.respondWith(
    caches.match(req).then(function(cached){
      if(cached){ return cached; }
      return fetch(req).then(function(response){
        if(response && response.status === 200 && response.type === "basic"){
          var copy = response.clone();
          caches.open(CACHE_NAME).then(function(c){ c.put(req, copy); });
        }
        return response;
      });
    })
  );
});
