// Google Cloud Storage returns 404 for non-root sites because no object exists.
// This can be fixed by forwarding 404-sites back to index.html. However, the return
// code in such case is 404, which is non-optimal for SEO.
// 
// E.g. https://jmyrberg.com/demo-projects/finscraper
// => Returns 404
// => Redirects browser into jmyrberg.com with given path /demo-projects/finscraper
// => User experience is OK as browser works fine, but 404 is not OK for SEO
//
// More information:
// https://issuetracker.google.com/issues/151212194
//
// The following is used as CloudFlare service worker to convert 404 into 200:
addEventListener('fetch', event => {
    event.respondWith(fetchAndLog(event.request))
})

async function fetchAndLog(req) {
    const res = await fetch(req)

    if (res.status === 404 && req.method === 'GET') {
        return new Response(res.body, {
            headers: res.headers,
            status: 200
        })
    }
    return res
}