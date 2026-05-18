# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test_demo.spec.ts >> locator API healing — Ghost heals silently
- Location: tests\test_demo.spec.ts:26:5

# Error details

```
TimeoutError: locator.apply: Timeout 5000ms exceeded.
Call log:
  - waiting for locator('#login-button-Broken')

```

# Page snapshot

```yaml
- generic [ref=e3]:
  - generic [ref=e4]: Swag Labs
  - generic [ref=e5]:
    - generic [ref=e9]:
      - textbox "Username" [ref=e11]: standard_user
      - textbox "Password" [active] [ref=e13]: secret_sauce
      - button "Login" [ref=e15] [cursor=pointer]
    - generic [ref=e17]:
      - generic [ref=e18]:
        - heading "Accepted usernames are:" [level=4] [ref=e19]
        - text: standard_user
        - text: locked_out_user
        - text: problem_user
        - text: performance_glitch_user
        - text: error_user
        - text: visual_user
      - generic [ref=e20]:
        - heading "Password for all users:" [level=4] [ref=e21]
        - text: secret_sauce
```

# Test source

```ts
  139 |       for (let i = 0; i < lines.length; i++) {
  140 |         if (lines[i].includes(oldSelector)) {
  141 |           let upd = lines[i].replace(re, `$1${newSelector}$2`);
  142 |           if (upd === lines[i]) upd = lines[i].split(oldSelector).join(newSelector);
  143 |           lines[i] = upd; fixedLine = i + 1; fixed = true; break;
  144 |         }
  145 |       }
  146 |     }
  147 | 
  148 |     if (fixed) {
  149 |       fs.writeFileSync(filePath, lines.join('\n'), 'utf8');
  150 |       const rel = path.relative(process.cwd(), filePath);
  151 |       console.log(`[GHOST] 📝 SourceHealer patching: ${rel}:${fixedLine}`);
  152 |       console.log(`         OLD → '${oldSelector}'`);
  153 |       console.log(`         NEW → '${newSelector}'`);
  154 |       console.log(`[GHOST] ✅ Source permanently fixed.\n`);
  155 |     }
  156 |     return fixed;
  157 |   } catch (e) {
  158 |     console.error('[GHOST] SourceHealer error:', e.message);
  159 |     return false;
  160 |   }
  161 | }
  162 | 
  163 | // ── Core: Failure Handler ─────────────────────────────────────────────────────
  164 | //
  165 | // Called from every intercepted catch block.
  166 | // page        — Playwright Page object (for screenshot + content)
  167 | // selector    — the broken selector string
  168 | // action      — 'click', 'fill', etc.
  169 | 
  170 | async function handleFailure(page, selector, action) {
  171 |   const uuid       = genId();
  172 |   const callerInfo = findCallerFile();
  173 |   const url        = page.url();
  174 |   const wsRoot     = findWorkspaceRoot();
  175 |   const queueDir   = getQueueDir();
  176 |   const ssDir      = path.join(wsRoot, 'reports', 'ghost', 'screenshots');
  177 |   const htmlDir    = path.join(wsRoot, 'reports', 'ghost', 'html');
  178 | 
  179 |   fs.mkdirSync(queueDir, { recursive: true });
  180 |   fs.mkdirSync(ssDir,    { recursive: true });
  181 |   fs.mkdirSync(htmlDir,  { recursive: true });
  182 | 
  183 |   let screenshotPath = '';
  184 |   let htmlPath = '';
  185 |   
  186 |   try {
  187 |     const ssFile = path.join(ssDir, `${SESSION_ID}_${safeSelector(selector)}_${uuid}.png`);
  188 |     htmlPath = path.join(htmlDir, `${SESSION_ID}_${uuid}.html`);
  189 |     
  190 |     const [rawDom] = await Promise.all([
  191 |       page.content(),
  192 |       page.screenshot({ path: ssFile, fullPage: true }),
  193 |     ]);
  194 |     
  195 |     screenshotPath = ssFile;
  196 |     console.log(`[GHOST] 📸 Diagnostics captured.`);
  197 | 
  198 |     // Save HTML snapshot for the brain to use during teardown
  199 |     fs.writeFileSync(htmlPath, rawDom, 'utf8');
  200 |   } catch (diagErr) {
  201 |     console.warn(`[GHOST] ⚠️  Could not capture diagnostics: ${diagErr.message}`);
  202 |   }
  203 | 
  204 |   // Write failure entry to disk immediately
  205 |   const failureFile = path.join(queueDir, `failure_${uuid}.json`);
  206 |   fs.writeFileSync(failureFile, JSON.stringify({
  207 |     uuid, selector, action, url,
  208 |     file: callerInfo.file,
  209 |     line: callerInfo.line,
  210 |     timestamp: getISTTimestamp(),
  211 |     session_id: SESSION_ID,
  212 |     screenshot_path: screenshotPath,
  213 |     html_path: htmlPath,
  214 |   }), 'utf8');
  215 | 
  216 |   console.log(`[GHOST] 🔄 Queued for AI healing — brain contacted in background...`);
  217 |   console.log(`[GHOST] ⏳ Healing will be applied after the test suite finishes.\n`);
  218 | }
  219 | 
  220 | // ── Playwright Prototype Patcher ──────────────────────────────────────────────
  221 | 
  222 | function patchLocatorProto(locator) {
  223 |   const proto = Object.getPrototypeOf(locator);
  224 |   if (proto.__ghost_patched) return;
  225 |   proto.__ghost_patched = true;
  226 | 
  227 |   const methods = {
  228 |     click: 'click', fill: 'fill', hover: 'hover',
  229 |     check: 'check', uncheck: 'uncheck', dblclick: 'click',
  230 |     tap: 'click', selectOption: 'select', press: 'press',
  231 |     waitFor: 'wait',
  232 |   };
  233 | 
  234 |   for (const [method, action] of Object.entries(methods)) {
  235 |     if (typeof proto[method] !== 'function') continue;
  236 |     const original = proto[method];
  237 |     proto[method] = async function (...args) {
  238 |       try {
> 239 |         return await original.apply(this, args);
      |                               ^ TimeoutError: locator.apply: Timeout 5000ms exceeded.
  240 |       } catch (err) {
  241 |         const selector = this.__ghost_selector || String(this);
  242 |         const page     = this.__ghost_page;
  243 |         console.log(`\n[GHOST] ❌ Locator failure! '${selector}' → action '${action}' failed.`);
  244 |         if (page) await handleFailure(page, selector, action);
  245 |         throw err; // ← re-throw so Playwright marks test step as failed
  246 |       }
  247 |     };
  248 |   }
  249 | }
  250 | 
  251 | function patchPageProto(page) {
  252 |   if (page.__ghost_patched) return;
  253 |   page.__ghost_patched = true;
  254 | 
  255 |   const proto = Object.getPrototypeOf(page);
  256 | 
  257 |   // Patch direct page actions
  258 |   const methods = {
  259 |     click: 'click', fill: 'fill', hover: 'hover',
  260 |     check: 'check', uncheck: 'uncheck', dblclick: 'click',
  261 |     selectOption: 'select', press: 'press', waitForSelector: 'wait',
  262 |   };
  263 | 
  264 |   for (const [method, action] of Object.entries(methods)) {
  265 |     if (typeof proto[method] !== 'function' || proto[method].__ghost_patched) continue;
  266 |     const original = proto[method];
  267 |     proto[method] = async function (selector, ...args) {
  268 |       try {
  269 |         return await original.call(this, selector, ...args);
  270 |       } catch (err) {
  271 |         console.log(`\n[GHOST] ❌ Page.${method} failure! Selector '${selector}' failed.`);
  272 |         await handleFailure(this, selector, action);
  273 |         throw err;
  274 |       }
  275 |     };
  276 |     proto[method].__ghost_patched = true;
  277 |   }
  278 | 
  279 |   // Patch page.locator to attach page/selector metadata
  280 |   if (typeof proto.locator === 'function' && !proto.locator.__ghost_patched) {
  281 |     const origLocator = proto.locator;
  282 |     proto.locator = function (selector, ...args) {
  283 |       const loc = origLocator.call(this, selector, ...args);
  284 |       loc.__ghost_page     = this;
  285 |       loc.__ghost_selector = selector;
  286 |       patchLocatorProto(loc);
  287 |       return loc;
  288 |     };
  289 |     proto.locator.__ghost_patched = true;
  290 |   }
  291 | 
  292 |   console.log('[GHOST] ✅ Playwright Page & Locator self-healing activated (deferred-parallel mode).');
  293 | }
  294 | 
  295 | // ── Module._load Intercept ────────────────────────────────────────────────────
  296 | 
  297 | Module._load = function (request, parent, isMain) {
  298 |   const exports = originalLoad.apply(this, arguments);
  299 | 
  300 |   if ((request === 'playwright-core' || request === 'playwright') &&
  301 |        exports && exports.chromium && !exports.__ghost_patched) {
  302 |     exports.__ghost_patched = true;
  303 | 
  304 |     const origLaunch = exports.chromium.launch;
  305 |     exports.chromium.launch = async function (...args) {
  306 |       const browser = await origLaunch.apply(this, args);
  307 | 
  308 |       const origNewContext = browser.newContext;
  309 |       browser.newContext = async function (...cArgs) {
  310 |         const ctx = await origNewContext.apply(this, cArgs);
  311 |         const origNewPage = ctx.newPage;
  312 |         ctx.newPage = async function (...pArgs) {
  313 |           const page = await origNewPage.apply(this, pArgs);
  314 |           patchPageProto(page);
  315 |           return page;
  316 |         };
  317 |         return ctx;
  318 |       };
  319 | 
  320 |       const origBrowserNewPage = browser.newPage;
  321 |       browser.newPage = async function (...pArgs) {
  322 |         const page = await origBrowserNewPage.apply(this, pArgs);
  323 |         patchPageProto(page);
  324 |         return page;
  325 |       };
  326 | 
  327 |       return browser;
  328 |     };
  329 |   }
  330 | 
  331 |   return exports;
  332 | };
  333 | 
```