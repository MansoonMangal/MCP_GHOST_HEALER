/**
 * HealQA Universal JS Agent (Absolute Universality Edition)
 * This script runs inside the browser and provides a universal bridge 
 * for ANY tool (Selenium, Playwright, Cypress) in ANY language.
 */
const HealQA = {
    serverUrl: 'http://localhost:8000/api/heal-locator',

    /**
     * Captures the full DOM and essential metadata
     */
    getDomSnapshot: function () {
        return {
            html: document.documentElement.outerHTML,
            url: window.location.href,
            title: document.title
        };
    },

    /**
     * Highlights an element with a glowing gold border
     */
    highlight: function (selector) {
        const el = document.querySelector(selector);
        if (el) {
            el.style.outline = '4px solid #FFD700';
            el.style.outlineOffset = '2px';
            el.style.boxShadow = '0 0 15px #FFD700';
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    },

    /**
     * Captures the unique 'DNA' of an element for learning
     */
    getElementDNA: function (selector) {
        const el = document.querySelector(selector);
        if (!el) return null;
        return {
            tag: el.tagName.toLowerCase(),
            id: el.id,
            name: el.name,
            classes: Array.from(el.classList),
            text: el.innerText || el.value,
            type: el.getAttribute('type'),
            placeholder: el.getAttribute('placeholder'),
            path: this.getSimulatedXPath(el)
        };
    },

    getSimulatedXPath: function(el) {
        if (el.id!=='') return 'id("'+el.id+'")';
        if (el===document.body) return el.tagName;
        var ix= 0;
        var siblings= el.parentNode.childNodes;
        for (var i= 0; i<siblings.length; i++) {
            var sibling= siblings[i];
            if (sibling===el) return this.getSimulatedXPath(el.parentNode)+'/'+el.tagName+'['+(ix+1)+']';
            if (sibling.nodeType===1 && sibling.tagName===el.tagName) ix++;
        }
    },

    /**
     * THE MASTER ACTION: safePerform
     * Handles healing and action execution directly in the browser.
     */
    safePerform: async function (selector, action, value = null) {
        console.log(`[HealQA] Attempting ${action} on: ${selector}`);
        let el = document.querySelector(selector);

        if (!el) {
            console.warn(`[HealQA] Selector NOT FOUND: ${selector}. Initiating AI Healing...`);

            try {
                const snapshot = this.getDomSnapshot();
                const response = await fetch(this.serverUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        selector: selector,
                        dom_snapshot: snapshot.html,
                        page_url: snapshot.url,
                        action: (action === 'fill' || action === 'sendKeys') ? 'fill' : 'click',
                        test_name: 'Universal_JS_Agent_Run'
                    })
                });

                const data = await response.json();
                if (data.healed_locator) {
                    console.log(`✨ [HealQA] HEALED: ${selector} -> ${data.healed_locator}`);
                    el = document.querySelector(data.healed_locator);
                    this.highlight(data.healed_locator);
                }
            } catch (err) {
                console.error("[HealQA] Healing failed:", err);
            }
        }

        if (el) {
            if (action === 'fill' || action === 'sendKeys') {
                el.value = value;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                console.log(`[HealQA] Action ${action} completed on healed element.`);
            } else {
                el.click();
                console.log(`[HealQA] Action ${action} completed on healed element.`);
            }
            return true;
        } else {
            console.error(`[HealQA] Critical Failure: Element ${selector} could not be found or healed.`);
            return false;
        }
    }
};

window.HealQA = HealQA;
console.log("🚀 HealQA Universal Agent Loaded!");
