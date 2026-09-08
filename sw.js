var CACHE_NAME = "kosh-shell-v1";
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
        keys.filter(function(key){ return key !== CACHE_NAME; })
            .map(function(key){ return caches.delete(key); })
      );
    })
  );
  self.clients.claim();
});

// App shell: cache-first (works offline).
// Dictionary API calls: always go to the network (never cached, and the fetch
// handler ignores them) so lookups stay fresh.
self.addEventListener("fetch", function(event){
  var url = event.request.url;
  if(url.indexOf("api.dictionaryapi.dev") !== -1){
    return; // let the browser handle it directly
  }
  if(event.request.method !== "GET"){ return; }

  event.respondWith(
    caches.match(event.request).then(function(cached){
      if(cached){ return cached; }
      return fetch(event.request).then(function(response){
        if(response && response.status === 200 && response.type === "basic"){
          var copy = response.clone();
          caches.open(CACHE_NAME).then(function(cache){ cache.put(event.request, copy); });
        }
        return response;
      }).catch(function(){
        return caches.match("./index.html");
      });
    })
  );
});
