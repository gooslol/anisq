// Based on consumet.ts, modified by iiPython to remove axios dependency and other useless crap.
// https://github.com/consumet/consumet.ts

import { load } from "cheerio";
import CryptoJS from "crypto-js";

const USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36";

class GogoCDN {
    constructor() {
        this.referer = "";
        this.keys = {
            key: CryptoJS.enc.Utf8.parse("37911490979715163134003223491201"),
            secondKey: CryptoJS.enc.Utf8.parse("54674138327930866480207815084989"),
            iv: CryptoJS.enc.Utf8.parse("3134003223491201"),
        };
        this.sources = [];
        this.serverName = "goload";
    }

    async extract(videoUrl) {
        this.referer = videoUrl.href;

        const res = await fetch(videoUrl.href);
        const $ = load(await res.text());

        const encyptedParams = await this.generateEncryptedAjaxParams($, videoUrl.searchParams.get("id") ?? "");
        const encryptedData = await fetch(
            `${videoUrl.protocol}//${videoUrl.hostname}/encrypt-ajax.php?${encyptedParams}`,
            {
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            }
        );
        const decryptedData = await this.decryptAjaxData((await encryptedData.json()).data);
        if (!decryptedData.source) throw new Error("No source found. Try a different server.");
        if (decryptedData.source[0].file.includes(".m3u8")) {
            const resResult = await fetch(decryptedData.source[0].file.toString());
            const resolutions = (await resResult.text()).match(/(RESOLUTION=)(.*)(\s*?)(\s*.*)/g);
            resolutions?.forEach((res) => {
                const index = decryptedData.source[0].file.lastIndexOf("/");
                const quality = res.split("\n")[0].split("x")[1].split(",")[0];
                const url = decryptedData.source[0].file.slice(0, index);
                this.sources.push({
                    url: url + "/" + res.split("\n")[1],
                    isM3U8: (url + res.split("\n")[1]).includes(".m3u8"),
                    quality: quality + "p",
                });
            });
            decryptedData.source.forEach((source) => {
                this.sources.push({
                    url: source.file,
                    isM3U8: source.file.includes(".m3u8"),
                    quality: "default",
                });
            });
        } else {
            decryptedData.source.forEach((source) => {
                this.sources.push({
                    url: source.file,
                    isM3U8: source.file.includes(".m3u8"),
                    quality: source.label.split(" ")[0] + "p",
                });
            });
        }
        decryptedData.source_bk.forEach((source) => {
            this.sources.push({
                url: source.file,
                isM3U8: source.file.includes(".m3u8"),
                quality: "backup",
            });
        });
        return {
            sources: this.sources
        };
    };

    async addSources(source) {
        if (source.file.includes("m3u8")) {
            const m3u8Urls = await fetch(source.file, {
                headers: {
                    Referer: this.referer,
                    "User-Agent": USER_AGENT,
                },
            });
            const videoList = (await m3u8Urls.text()).split("#EXT-X-I-FRAME-STREAM-INF:");
            for (const video of videoList ?? []) {
                if (!video.includes("m3u8")) continue;
                const url = video
                    .split("\n")
                    .find((line) => line.includes("URI="))
                    .split("URI=")[1]
                    .replace(/'/g, "");

                const quality = video.split("RESOLUTION=")[1].split(",")[0].split("x")[1];
                this.sources.push({ url: url, quality: `${quality}p`, isM3U8: true });
            }
            return;
        }
        this.sources.push({
            url: source.file,
            isM3U8: source.file.includes(".m3u8"),
        });
    };
    async generateEncryptedAjaxParams($, id) {
        const encryptedKey = CryptoJS.AES.encrypt(id, this.keys.key, { iv: this.keys.iv });
        const scriptValue = $(`script[data-name="episode"]`).attr("data-value");
        const decryptedToken = CryptoJS.AES.decrypt(scriptValue, this.keys.key, { iv: this.keys.iv }).toString(CryptoJS.enc.Utf8);
        return `id=${encryptedKey}&alias=${id}&${decryptedToken}`;
    };
    async decryptAjaxData(encryptedData) {
        const decryptedData = CryptoJS.enc.Utf8.stringify(CryptoJS.AES.decrypt(encryptedData, this.keys.secondKey, { iv: this.keys.iv }));
        return JSON.parse(decryptedData);
    };
}

class Gogoanime {
    constructor() {
        this.baseUrl = "https://anitaku.bz/";
        this.ajaxUrl = "https://ajax.gogocdn.net/ajax";
    }

    async search(query, page = 1) {
        const searchResult = {
            currentPage: page,
            hasNextPage: false,
            results: [],
        };
        const res = await fetch(`${this.baseUrl}/filter.html?keyword=${encodeURIComponent(query)}&page=${page}`);
        const $ = load(await res.text());
        searchResult.hasNextPage = $("div.anime_name.new_series > div > div > ul > li.selected").next().length > 0;
        $("div.last_episodes > ul > li").each((i, el) => {
            searchResult.results.push({
                id: $(el).find("p.name > a").attr("href")?.split("/")[2],
                title: $(el).find("p.name > a").text(),
                url: `${this.baseUrl}/${$(el).find("p.name > a").attr("href")}`,
                releaseDate: $(el).find("p.released").text().trim().replace("Released: ", ""),
            });
        });
        return searchResult;
    };

    async fetchAnimeInfo(id) {
        if (!id.includes("gogoanime")) id = `${this.baseUrl}/category/${id}`;

        const animeInfo = {
            id: "",
            title: "",
            url: "",
            genres: [],
            totalEpisodes: 0,
        };
        const res = await fetch(id);

        const $ = load(await res.text());

        animeInfo.id = new URL(id).pathname.split("/")[2];
        animeInfo.title = $(
            "section.content_left > div.main_body > div:nth-child(2) > div.anime_info_body_bg > h1"
        )
            .text()
            .trim();
        animeInfo.url = id;
        animeInfo.releaseDate = $("div.anime_info_body_bg > p:nth-child(8)")
            .text()
            .trim()
            .split("Released: ")[1];
        animeInfo.description = $("div.anime_info_body_bg > div:nth-child(6)")
            .text()
            .trim()
            .replace("Plot Summary: ", "");

        animeInfo.type = $("div.anime_info_body_bg > p:nth-child(4) > a")
            .text()
            .trim()
            .toUpperCase();

        animeInfo.otherName = $(".other-name a").text().trim();
        const ep_start = $("#episode_page > li").first().find("a").attr("ep_start");
        const ep_end = $("#episode_page > li").last().find("a").attr("ep_end");
        const movie_id = $("#movie_id").attr("value");
        const alias = $("#alias_anime").attr("value");
        const html = await fetch(
            `${this.ajaxUrl}/load-list-episode?ep_start=${ep_start}&ep_end=${ep_end}&id=${movie_id}&default_ep=${0}&alias=${alias}`
        );
        const $$ = load(await html.text());
        animeInfo.episodes = [];
        $$("#episode_related > li").each((i, el) => {
            animeInfo.episodes?.push({
                id: $(el).find("a").attr("href")?.split("/")[1],
                number: parseFloat($(el).find(`div.name`).text().replace("EP ", "")),
                url: `${this.baseUrl}/${$(el).find(`a`).attr("href")?.trim()}`,
            });
        });
        animeInfo.episodes = animeInfo.episodes.reverse();
        animeInfo.totalEpisodes = parseInt(ep_end ?? "0");
        return animeInfo;
    };
    async fetchEpisodeSources(episodeId, downloadUrl) {
        if (episodeId.startsWith("http")) {
            const serverUrl = new URL(episodeId);
            return {
                headers: { Referer: serverUrl.origin },
                ...(await new GogoCDN(this.proxyConfig, this.adapter).extract(serverUrl)),
                download: downloadUrl ? downloadUrl : `https://${serverUrl.host}/download${serverUrl.search}`,
            };
        }
        const res = await fetch(`${this.baseUrl}/${episodeId}`);
        const $ = load(await res.text());

        let serverUrl = new URL(`${$("#load_anime > div > div > iframe").attr("src")}`);

        const downloadLink = `${$(".dowloads > a").attr("href")}`;
        return downloadLink
            ? await this.fetchEpisodeSources(serverUrl.href, downloadLink)
            : await this.fetchEpisodeSources(serverUrl.href);
    };
}

export default Gogoanime;
