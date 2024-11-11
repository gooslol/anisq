// Copyright (c) 2024 iiPython

import Gogoanime from "./provider";

const anime = new Gogoanime()

export default {
    async fetch(req) {
        const url = new URL(req.url);
        switch (url.pathname) {
            case "/":
                return Response.redirect("https://github.com/gooslol/anisq", 301);
    
            case "/v1/search":
                const query = url.searchParams.get("q");
                if (!query) return new Response("Missing query.");
                return Response.json((await anime.search(query)).results);
    
            case "/v1/info":
                const item = url.searchParams.get("id");
                if (!item) return new Response("Missing item id.");
                return Response.json((await anime.fetchAnimeInfo(item)));
    
            case "/v1/watch":
                const episode = url.searchParams.get("id");
                if (!episode) return new Response("Missing episode id.");
                return Response.json((await anime.fetchEpisodeSources(episode)));
    
            default:
                return new Response("Not found.");
        }
    }
}
