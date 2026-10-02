(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push(["object" == typeof document ? document.currentScript : void 0, 22016, (e, t, r) => {
  "use strict";
  e.i(47167), Object.defineProperty(r, "__esModule", {
    value: !0
  });
  var n = {
    default: function() {
      return b
    },
    useLinkStatus: function() {
      return v
    }
  };
  for (var a in n) Object.defineProperty(r, a, {
    enumerable: !0,
    get: n[a]
  });
  let s = e.r(90809),
    i = e.r(43476),
    l = s._(e.r(71645)),
    c = e.r(95057),
    o = e.r(8372),
    d = e.r(18581),
    x = e.r(18967),
    u = e.r(5550),
    m = e.r(88540),
    p = e.r(91949),
    f = e.r(73668),
    h = e.r(9396);

  function b(t) {
    var r;
    let n, a, s, [b, v] = (0, l.useOptimistic)(p.IDLE_LINK_STATUS),
      j = (0, l.useRef)(null),
      {
        href: N,
        as: y,
        children: z,
        prefetch: w = null,
        passHref: k,
        replace: S,
        shallow: C,
        scroll: $,
        onClick: P,
        onMouseEnter: E,
        onTouchStart: _,
        legacyBehavior: T = !1,
        onNavigate: O,
        transitionTypes: A,
        ref: R,
        unstable_dynamicOnHover: I,
        ...U
      } = t;
    n = z, T && ("string" == typeof n || "number" == typeof n) && (n = (0, i.jsx)("a", {
      children: n
    }));
    let B = l.default.useContext(o.AppRouterContext),
      F = !1 !== w,
      L = !1 === w ? "none" : !0 === w ? "full" : "auto",
      M = "none" !== L ? "auto" === L ? h.FetchStrategy.PPR : h.FetchStrategy.Full : h.FetchStrategy.PPR,
      D = "string" == typeof(r = y || N) ? r : (0, c.formatUrl)(r);
    if (T) {
      if (n?.$$typeof === Symbol.for("react.lazy")) throw Object.defineProperty(Error("`<Link legacyBehavior>` received a direct child that is either a Server Component, or JSX that was loaded with React.lazy(). This is not supported. Either remove legacyBehavior, or make the direct child a Client Component that renders the Link's `<a>` tag."), "__NEXT_ERROR_CODE", {
        value: "E863",
        enumerable: !1,
        configurable: !0
      });
      a = l.default.Children.only(n)
    }
    let W = T ? a && "object" == typeof a && a.ref : R,
      K, V = l.default.useCallback(e => (null !== B && (j.current = (0, p.mountLinkInstance)(e, D, B, M, F, v, K)), () => {
        j.current && ((0, p.unmountLinkForCurrentNavigation)(j.current), j.current = null), (0, p.unmountPrefetchableInstance)(e)
      }), [F, D, B, M, v, K]),
      X = {
        ref: (0, d.useMergedRef)(V, W),
        onClick(t) {
          T || "function" != typeof P || P(t), T && a.props && "function" == typeof a.props.onClick && a.props.onClick(t), !B || t.defaultPrevented || function(t, r, n, a, s, i, c, o = "none") {
            if ("u" > typeof window) {
              let d, {
                nodeName: x
              } = t.currentTarget;
              if ("A" === x.toUpperCase() && ((d = t.currentTarget.getAttribute("target")) && "_self" !== d || t.metaKey || t.ctrlKey || t.shiftKey || t.altKey || t.nativeEvent && 2 === t.nativeEvent.which) || t.currentTarget.hasAttribute("download")) return;
              if (!(0, f.isLocalURL)(r)) {
                a && (t.preventDefault(), location.replace(r));
                return
              }
              if (t.preventDefault(), i) {
                let e = !1;
                if (i({
                    preventDefault: () => {
                      e = !0
                    }
                  }), e) return
              }
              let {
                dispatchNavigateAction: u
              } = e.r(99781);
              l.default.startTransition(() => {
                u(r, a ? "replace" : "push", !1 === s ? m.ScrollBehavior.NoScroll : m.ScrollBehavior.Default, n.current, c, o)
              })
            }
          }(t, D, j, S, $, O, A, L)
        },
        onMouseEnter(e) {
          T || "function" != typeof E || E(e), T && a.props && "function" == typeof a.props.onMouseEnter && a.props.onMouseEnter(e), B && F && (0, p.onNavigationIntent)(e.currentTarget, !0 === I)
        },
        onTouchStart: function(e) {
          T || "function" != typeof _ || _(e), T && a.props && "function" == typeof a.props.onTouchStart && a.props.onTouchStart(e), B && F && (0, p.onNavigationIntent)(e.currentTarget, !0 === I)
        }
      };
    return (0, x.isAbsoluteUrl)(D) ? X.href = D : T && !k && ("a" !== a.type || "href" in a.props) || (X.href = (0, u.addBasePath)(D)), s = T ? l.default.cloneElement(a, X) : (0, i.jsx)("a", {
      ...U,
      ...X,
      children: n
    }), (0, i.jsx)(g.Provider, {
      value: b,
      children: s
    })
  }
  let g = (0, l.createContext)(p.IDLE_LINK_STATUS),
    v = () => (0, l.useContext)(g);
  ("function" == typeof r.default || "object" == typeof r.default && null !== r.default) && void 0 === r.default.__esModule && (Object.defineProperty(r.default, "__esModule", {
    value: !0
  }), Object.assign(r.default, r), t.exports = r.default)
}, 18581, (e, t, r) => {
  "use strict";
  Object.defineProperty(r, "__esModule", {
    value: !0
  }), Object.defineProperty(r, "useMergedRef", {
    enumerable: !0,
    get: function() {
      return a
    }
  });
  let n = e.r(71645);

  function a(e, t) {
    let r = (0, n.useRef)(null),
      a = (0, n.useRef)(null);
    return (0, n.useCallback)(n => {
      if (null === n) {
        let e = r.current;
        e && (r.current = null, e());
        let t = a.current;
        t && (a.current = null, t())
      } else e && (r.current = s(e, n)), t && (a.current = s(t, n))
    }, [e, t])
  }

  function s(e, t) {
    if ("function" != typeof e) return e.current = t, () => {
      e.current = null
    };
    {
      let r = e(t);
      return "function" == typeof r ? r : () => e(null)
    }
  }("function" == typeof r.default || "object" == typeof r.default && null !== r.default) && void 0 === r.default.__esModule && (Object.defineProperty(r.default, "__esModule", {
    value: !0
  }), Object.assign(r.default, r), t.exports = r.default)
}, 18967, (e, t, r) => {
  "use strict";
  e.i(47167), Object.defineProperty(r, "__esModule", {
    value: !0
  });
  var n = {
    DecodeError: function() {
      return b
    },
    MiddlewareNotFoundError: function() {
      return N
    },
    MissingStaticPage: function() {
      return j
    },
    NormalizeError: function() {
      return g
    },
    PageNotFoundError: function() {
      return v
    },
    SP: function() {
      return f
    },
    ST: function() {
      return h
    },
    WEB_VITALS: function() {
      return s
    },
    execOnce: function() {
      return i
    },
    getDisplayName: function() {
      return x
    },
    getLocationOrigin: function() {
      return o
    },
    getURL: function() {
      return d
    },
    isAbsoluteUrl: function() {
      return c
    },
    isResSent: function() {
      return u
    },
    loadGetInitialProps: function() {
      return p
    },
    normalizeRepeatedSlashes: function() {
      return m
    },
    stringifyError: function() {
      return y
    }
  };
  for (var a in n) Object.defineProperty(r, a, {
    enumerable: !0,
    get: n[a]
  });
  let s = ["CLS", "FCP", "FID", "INP", "LCP", "TTFB"];

  function i(e) {
    let t, r = !1;
    return (...n) => (r || (r = !0, t = e(...n)), t)
  }
  let l = /^[a-zA-Z][a-zA-Z\d+\-.]*?:/,
    c = e => {
      let t = e.charCodeAt(0);
      return !!(t >= 65 && t <= 90 || t >= 97 && t <= 122) && l.test(e)
    };

  function o() {
    let {
      protocol: e,
      hostname: t,
      port: r
    } = window.location;
    return `${e}//${t}${r?":"+r:""}`
  }

  function d() {
    let {
      href: e
    } = window.location, t = o();
    return e.substring(t.length)
  }

  function x(e) {
    return "string" == typeof e ? e : e.displayName || e.name || "Unknown"
  }

  function u(e) {
    return e.finished || e.headersSent
  }

  function m(e) {
    let t = e.split("?");
    return t[0].replace(/\\/g, "/").replace(/\/\/+/g, "/") + (t[1] ? `?${t.slice(1).join("?")}` : "")
  }
  async function p(e, t) {
    let r = t.res || t.ctx && t.ctx.res;
    if (!e.getInitialProps) return t.ctx && t.Component ? {
      pageProps: await p(t.Component, t.ctx)
    } : {};
    let n = await e.getInitialProps(t);
    if (r && u(r)) return n;
    if (!n) throw Object.defineProperty(Error(`"${x(e)}.getInitialProps()" should resolve to an object. But found "${n}" instead.`), "__NEXT_ERROR_CODE", {
      value: "E1025",
      enumerable: !1,
      configurable: !0
    });
    return n
  }
  let f = "u" > typeof performance,
    h = f && ["mark", "measure", "getEntriesByName"].every(e => "function" == typeof performance[e]);
  class b extends Error {}
  class g extends Error {}
  class v extends Error {
    constructor(e) {
      super(), this.code = "ENOENT", this.name = "PageNotFoundError", this.message = `Cannot find module for page: ${e}`
    }
  }
  class j extends Error {
    constructor(e, t) {
      super(), this.message = `Failed to load static file for page: ${e} ${t}`
    }
  }
  class N extends Error {
    constructor() {
      super(), this.code = "ENOENT", this.message = "Cannot find the middleware module"
    }
  }

  function y(e) {
    return JSON.stringify({
      message: e.message,
      stack: e.stack
    })
  }
}, 73668, (e, t, r) => {
  "use strict";
  Object.defineProperty(r, "__esModule", {
    value: !0
  }), Object.defineProperty(r, "isLocalURL", {
    enumerable: !0,
    get: function() {
      return s
    }
  });
  let n = e.r(18967),
    a = e.r(52817);

  function s(e) {
    if (!(0, n.isAbsoluteUrl)(e)) return !0;
    try {
      let t = (0, n.getLocationOrigin)(),
        r = new URL(e, t);
      return r.origin === t && (0, a.hasBasePath)(r.pathname)
    } catch (e) {
      return !1
    }
  }
}, 98183, (e, t, r) => {
  "use strict";
  Object.defineProperty(r, "__esModule", {
    value: !0
  });
  var n = {
    assign: function() {
      return c
    },
    searchParamsToUrlQuery: function() {
      return s
    },
    urlQueryToSearchParams: function() {
      return l
    }
  };
  for (var a in n) Object.defineProperty(r, a, {
    enumerable: !0,
    get: n[a]
  });

  function s(e) {
    let t = {};
    for (let [r, n] of e.entries()) {
      let e = t[r];
      void 0 === e ? t[r] = n : Array.isArray(e) ? e.push(n) : t[r] = [e, n]
    }
    return t
  }

  function i(e) {
    return "string" == typeof e ? e : ("number" != typeof e || isNaN(e)) && "boolean" != typeof e ? "" : String(e)
  }

  function l(e) {
    let t = new URLSearchParams;
    for (let [r, n] of Object.entries(e))
      if (Array.isArray(n))
        for (let e of n) t.append(r, i(e));
      else t.set(r, i(n));
    return t
  }

  function c(e, ...t) {
    for (let r of t) {
      for (let t of r.keys()) e.delete(t);
      for (let [t, n] of r.entries()) e.append(t, n)
    }
    return e
  }
}, 95057, (e, t, r) => {
  "use strict";
  e.i(47167), Object.defineProperty(r, "__esModule", {
    value: !0
  });
  var n = {
    formatUrl: function() {
      return l
    },
    formatWithValidation: function() {
      return o
    },
    urlObjectKeys: function() {
      return c
    }
  };
  for (var a in n) Object.defineProperty(r, a, {
    enumerable: !0,
    get: n[a]
  });
  let s = e.r(90809)._(e.r(98183)),
    i = /https?|ftp|gopher|file/;

  function l(e) {
    let {
      auth: t,
      hostname: r
    } = e, n = e.protocol || "", a = e.pathname || "", l = e.hash || "", c = e.query || "", o = !1;
    t = t ? encodeURIComponent(t).replace(/%3A/i, ":") + "@" : "", e.host ? o = t + e.host : r && (o = t + (~r.indexOf(":") ? `[${r}]` : r), e.port && (o += ":" + e.port)), c && "object" == typeof c && (c = String(s.urlQueryToSearchParams(c)));
    let d = e.search || c && `?${c}` || "";
    return n && !n.endsWith(":") && (n += ":"), e.slashes || (!n || i.test(n)) && !1 !== o ? (o = "//" + (o || ""), a && "/" !== a[0] && (a = "/" + a)) : o || (o = ""), l && "#" !== l[0] && (l = "#" + l), d && "?" !== d[0] && (d = "?" + d), a = a.replace(/[?#]/g, encodeURIComponent), d = d.replace("#", "%23"), `${n}${o}${a}${d}${l}`
  }
  let c = ["auth", "hash", "host", "hostname", "href", "path", "pathname", "port", "protocol", "query", "search", "slashes"];

  function o(e) {
    return l(e)
  }
}, 53948, e => {
  "use strict";
  var t = e.i(43476),
    r = e.i(71645),
    n = e.i(15288),
    a = e.i(87486),
    s = e.i(93479),
    i = e.i(91918),
    l = e.i(25913),
    c = e.i(75157);
  let o = (0, l.cva)("inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive", {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground shadow-xs hover:bg-primary/90",
        destructive: "bg-destructive text-white shadow-xs hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
        outline: "border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground dark:bg-input/30 dark:border-input dark:hover:bg-input/50",
        secondary: "bg-secondary text-secondary-foreground shadow-xs hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50",
        link: "text-primary underline-offset-4 hover:underline"
      },
      size: {
        default: "h-9 px-4 py-2 has-[>svg]:px-3",
        sm: "h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5",
        lg: "h-10 rounded-md px-6 has-[>svg]:px-4",
        icon: "size-9"
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default"
    }
  });

  function d({
    className: e,
    variant: r,
    size: n,
    asChild: a = !1,
    ...s
  }) {
    let l = a ? i.Slot : "button";
    return (0, t.jsx)(l, {
      "data-slot": "button",
      className: (0, c.cn)(o({
        variant: r,
        size: n,
        className: e
      })),
      ...s
    })
  }
  let x = {
    SA: "🇸🇦 السعودية — ر.س",
    YE: "🇾🇪 اليمن — $",
    WW: "🌍 دولي — $"
  };

  function u(e, t) {
    return "SAR" === t ? `${e} ر.س` : `$${e.toFixed(2)}`
  }
  async function m(e, t) {
    return (await fetch(e, t ? {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(t)
    } : void 0)).json()
  }
  let p = {
    ps: "AI/SaaS",
    turgame: "بث وبطاقات"
  };

  function f({
    data: e,
    region: i,
    hasPhone: l,
    onBuy: c,
    onRefresh: o
  }) {
    let [x, m] = (0, r.useState)("الكل"), [h, b] = (0, r.useState)(""), g = (0, r.useMemo)(() => {
      let t = e.products;
      return "الكل" !== x && (t = t.filter(e => e.family === x)), h.trim() && (t = t.filter(e => e.name.toLowerCase().includes(h.trim().toLowerCase()))), t
    }, [e.products, x, h]);
    return (0, t.jsx)(n.Card, {
      className: "bg-zinc-900/60 border-zinc-800",
      children: (0, t.jsxs)(n.CardContent, {
        className: "p-3 space-y-3",
        children: [(0, t.jsxs)("div", {
          className: "flex flex-wrap items-center gap-2",
          children: [(0, t.jsxs)("div", {
            className: "text-sm font-bold text-zinc-100",
            children: ["🛒 المتجر — ", e.products.length, " منتجًا من عالمين"]
          }), (0, t.jsx)(d, {
            size: "sm",
            variant: "ghost",
            className: "text-[10px] text-zinc-500 h-7",
            onClick: o,
            children: "🔄 تحديث المزامنة"
          })]
        }), (0, t.jsxs)("div", {
          className: "flex flex-wrap gap-1.5 items-center",
          children: [(0, t.jsx)(s.Input, {
            dir: "rtl",
            className: "flex-1 min-w-40 h-9 text-xs bg-zinc-950 border-zinc-700",
            placeholder: "ابحث عن منتج… (ChatGPT، شاهد، Steam…)",
            value: h,
            onChange: e => b(e.target.value)
          }), ["الكل", ...e.families].map(e => (0, t.jsx)("button", {
            onClick: () => m(e),
            className: `text-[10.5px] rounded-full border px-2.5 py-1.5 transition-colors ${x===e?"border-emerald-600 bg-emerald-950/70 text-emerald-300":"border-zinc-700 bg-zinc-950 text-zinc-400 hover:border-zinc-600"}`,
            children: e
          }, e))]
        }), (0, t.jsx)("div", {
          className: "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5",
          children: g.map(e => {
            let r, n = e.prices[i] ?? e.prices.WW,
              s = 0 === (r = e.chain.filter(e => 0 !== e.stock)).length ? {
                ok: !1,
                label: "نفد حاليًا"
              } : null == r[0].stock ? {
                ok: !0,
                label: "متوفر (يُتحقق لحظة الطلب)"
              } : {
                ok: !0,
                label: `متوفر — ${r.length} ${r.length>1?"موردين":"مورد"}`
              },
              l = e.officialUsd && "USD" === n.currency && e.officialUsd > 2.5 * n.price ? Math.round((1 - n.price / e.officialUsd) * 100) : null;
            return (0, t.jsxs)("div", {
              className: `rounded border border-zinc-800 bg-zinc-950/70 p-3 flex flex-col gap-2 ${s.ok?"":"opacity-60"}`,
              children: [(0, t.jsxs)("div", {
                className: "flex items-start justify-between gap-2",
                children: [(0, t.jsx)("div", {
                  className: "text-[12.5px] font-bold text-zinc-100 leading-5",
                  children: e.name
                }), (0, t.jsx)(a.Badge, {
                  variant: "outline",
                  className: "text-[8.5px] shrink-0 border-zinc-700 bg-zinc-900 text-zinc-400",
                  children: p[e.sourceTier] ?? e.sourceTier
                })]
              }), (0, t.jsxs)("div", {
                className: "flex items-center justify-between gap-2",
                children: [(0, t.jsx)("div", {
                  className: "text-lg font-mono font-bold text-emerald-400",
                  dir: "ltr",
                  children: u(n.price, n.currency)
                }), null != l && (0, t.jsxs)(a.Badge, {
                  className: "text-[9px] bg-rose-950/70 text-rose-300 border border-rose-800",
                  variant: "outline",
                  children: ["−", l, "% رسمي"]
                })]
              }), (0, t.jsxs)("div", {
                className: "flex items-center justify-between gap-2",
                children: [(0, t.jsxs)("span", {
                  className: `text-[10px] ${s.ok?"text-emerald-500":"text-rose-400"}`,
                  children: ["● ", s.label]
                }), (0, t.jsx)("span", {
                  className: "text-[9px] text-zinc-600",
                  children: e.chain.length > 1 ? `سلسلة ${e.chain.length} موردين` : "مورد واحد"
                })]
              }), (0, t.jsx)(d, {
                className: "w-full h-10 text-xs bg-emerald-900 hover:bg-emerald-800 text-emerald-100 disabled:opacity-50",
                disabled: !s.ok,
                onClick: () => c(e),
                children: s.ok ? "🛒 اشترِ الآن — تسليم ≤3 دقائق" : "نفد — فعّل تنبيه التوفير"
              })]
            }, e.slug)
          })
        }), !l && (0, t.jsx)("div", {
          className: "text-[10.5px] text-amber-400 bg-amber-950/30 border border-amber-900/50 rounded px-2.5 py-1.5",
          children: "⚠️ الأسعار معروضة بالدولار العالمي — سجّل جوالك (+966 / +967) لتحصل على سعر منطقتك"
        }), (0, t.jsx)("div", {
          className: "text-[10px] text-zinc-600 leading-4",
          children: "الأسعار مقفلة لحظة الشراء · التسليم آلي عبر الموجّه متعدد الموردين · الوضع التجريبي يسلّم إيصالات موسومة (SANDBOX) والوضع الحي يشتري من ProdSeller فورًا"
        })]
      })
    })
  }
  let h = [{
    id: "wallet",
    name: "👛 المحفظة",
    desc: "خصم فوري + كاش باك 1% + استرداد لحظي — الأسرع"
  }, {
    id: "trc20",
    name: "💵 USDT TRC-20",
    desc: "أرسل للعنوان المعروض — تأكيد ببلوك واحد (~1-3 د) — رسوم شبكة ~$1"
  }, {
    id: "binance_pay",
    name: "🔵 Binance Pay",
    desc: "تأكيد لحظي 0 رسوم — يتطلب حساب تاجر عند التفعيل الحي"
  }];

  function b({
    product: e,
    phone: s,
    region: i,
    balance: l,
    onDone: c,
    onCancel: o,
    onNeedWallet: p
  }) {
    let [f, g] = (0, r.useState)("wallet"), [v, j] = (0, r.useState)(!1), [N, y] = (0, r.useState)(null), [z, w] = (0, r.useState)(null), k = e.prices[i] ?? e.prices.WW, S = "SA" === i ? Number((k.price / 3.75).toFixed(2)) : Number(k.price.toFixed(2)), C = null != l && l >= S, $ = async () => {
      if (!s) return void y("سجّل رقم جوالك أولًا");
      j(!0), y(null);
      let t = await m("/api/store/checkout", {
        slug: e.slug,
        phone: s,
        rail: f
      });
      (j(!1), t.ok) ? t.payment ? (w(t.payment), E(t.publicId)) : c(t.publicId): y(t.error || "خطأ غير متوقع")
    }, [P, E] = (0, r.useState)(null);
    return (0, t.jsx)(n.Card, {
      className: "bg-zinc-900/60 border-emerald-900/50",
      children: (0, t.jsxs)(n.CardContent, {
        className: "p-4 space-y-3",
        children: [(0, t.jsxs)("div", {
          className: "flex items-center justify-between",
          children: [(0, t.jsx)("div", {
            className: "text-sm font-bold text-zinc-100",
            children: "🔒 إتمام الشراء — سعر مقفل مضمون"
          }), (0, t.jsx)(d, {
            size: "sm",
            variant: "ghost",
            className: "text-xs text-zinc-500 h-8",
            onClick: o,
            children: "→ رجوع للمتجر"
          })]
        }), (0, t.jsxs)("div", {
          className: "rounded border border-zinc-800 bg-zinc-950/70 p-3 space-y-1.5",
          children: [(0, t.jsxs)("div", {
            className: "flex items-center justify-between",
            children: [(0, t.jsx)("span", {
              className: "text-[13px] font-bold text-zinc-100",
              children: e.name
            }), (0, t.jsx)(a.Badge, {
              variant: "outline",
              className: "text-[9px] border-zinc-700 text-zinc-400",
              children: e.family
            })]
          }), (0, t.jsxs)("div", {
            className: "flex items-center justify-between text-[11px]",
            children: [(0, t.jsx)("span", {
              className: "text-zinc-500",
              children: x[i]
            }), (0, t.jsxs)("div", {
              className: "flex items-center gap-2",
              children: ["SA" === i && (0, t.jsxs)("span", {
                className: "text-zinc-600 text-[10px]",
                dir: "ltr",
                children: ["≈ $", S.toFixed(2)]
              }), (0, t.jsx)("span", {
                className: "text-xl font-mono font-bold text-emerald-400",
                dir: "ltr",
                children: u(k.price, k.currency)
              })]
            })]
          }), (0, t.jsx)("div", {
            className: "text-[10px] text-zinc-600",
            children: "🔒 هذا السعر مقفول لطلبك — حتى لو تغيرت الأسعار بعده"
          })]
        }), z ? (0, t.jsxs)("div", {
          className: "rounded border border-amber-800/60 bg-amber-950/30 p-3 space-y-2",
          children: [(0, t.jsxs)("div", {
            className: "text-[12px] font-bold text-amber-300",
            children: ["📥 تعليمات الدفع (", z.network, ")"]
          }), (0, t.jsxs)("div", {
            className: "text-[10.5px] text-zinc-300 leading-5",
            children: ["العنوان: ", (0, t.jsx)("span", {
              className: "font-mono text-cyan-300 break-all",
              dir: "ltr",
              children: z.address
            }), (0, t.jsx)("br", {}), "المبلغ بالضبط: ", (0, t.jsxs)("span", {
              className: "font-mono text-emerald-300",
              dir: "ltr",
              children: ["$", z.amount.toFixed(2)]
            }), (0, t.jsx)("span", {
              className: "text-zinc-500",
              children: " (السنتات المميزة تربط التحويل بطلبك)"
            })]
          }), (0, t.jsx)("div", {
            className: "text-[10px] text-zinc-500 leading-4",
            children: z.instructions
          }), (0, t.jsx)(d, {
            className: "w-full h-11 bg-emerald-800 hover:bg-emerald-700 text-emerald-50",
            onClick: () => c(P),
            children: "▶️ محاكاة تأكيد الدفع (sandbox) — نفس مسار الـwebhook الحقيقي"
          })]
        }) : (0, t.jsxs)(t.Fragment, {
          children: [(0, t.jsx)("div", {
            className: "space-y-1.5",
            children: h.map(e => {
              let r = "wallet" === e.id && !C;
              return (0, t.jsxs)("button", {
                onClick: () => !r && g(e.id),
                className: `w-full text-right rounded border px-3 py-2.5 transition-colors ${f===e.id?"border-emerald-600 bg-emerald-950/50":"border-zinc-800 bg-zinc-950/60 hover:border-zinc-700"} ${r?"opacity-50":""}`,
                children: [(0, t.jsxs)("div", {
                  className: "flex items-center justify-between gap-2",
                  children: [(0, t.jsx)("span", {
                    className: "text-[12.5px] font-bold text-zinc-100",
                    children: e.name
                  }), "wallet" === e.id && (0, t.jsxs)("span", {
                    className: `text-[10px] font-mono ${C?"text-emerald-400":"text-rose-400"}`,
                    dir: "ltr",
                    children: [null != l ? `$${l.toFixed(2)}` : "—", " / $ ", S.toFixed(2)]
                  })]
                }), (0, t.jsx)("div", {
                  className: "text-[10.5px] text-zinc-500 leading-4 mt-0.5",
                  children: e.desc
                })]
              }, e.id)
            })
          }), "wallet" === f && !C && (0, t.jsx)(d, {
            variant: "outline",
            className: "w-full h-10 text-xs border-amber-700 text-amber-300",
            onClick: p,
            children: "الرصيد غير كافٍ — اشحن المحفظة (إيداع تجريبي فوري في sandbox)"
          }), N && (0, t.jsx)("div", {
            className: "text-[11px] text-rose-400 bg-rose-950/40 border border-rose-900/50 rounded px-2.5 py-1.5",
            children: N
          }), (0, t.jsx)(d, {
            className: "w-full h-12 text-sm font-bold bg-emerald-800 hover:bg-emerald-700 text-emerald-50",
            disabled: v || "wallet" === f && !C,
            onClick: $,
            children: v ? "⏳ جارٍ الإنشاء…" : "wallet" === f ? "🚀 ادفع من المحفظة وشراء المورد يبدأ فورًا" : "📝 إنشاء الطلب وتعليمات الدفع"
          })]
        }), (0, t.jsx)("div", {
          className: "text-[10px] text-zinc-600 leading-4",
          children: "بالضغط أنت توافق على: التسليم آلي عبر سلسلة الموردين (قد يتبدّل المورد تلقائيًا عند النفاد بنفس الجودة) · الفشل الكامل = استرداد لحظي + رصيد اعتذار $1"
        })]
      })
    })
  }
  let g = {
      ok: "✅",
      skip: "⏭️",
      fail: "❌"
    },
    v = {
      pending_payment: "border-amber-700 bg-amber-950/60 text-amber-300",
      paid: "border-cyan-700 bg-cyan-950/60 text-cyan-300",
      routing: "border-violet-700 bg-violet-950/60 text-violet-300",
      delivered: "border-emerald-700 bg-emerald-950/60 text-emerald-300",
      failed: "border-rose-800 bg-rose-950/60 text-rose-300"
    };

  function j({
    publicId: e,
    phone: s,
    onBack: i,
    onWalletRefresh: l
  }) {
    let [c, o] = (0, r.useState)(null), [x, u] = (0, r.useState)([]), [p, f] = (0, r.useState)(null), [h, b] = (0, r.useState)(!1), N = (0, r.useRef)(null), y = async () => {
      let t = await m(`/api/store/orders/${e}`);
      return t.ok && (o(t.order), u(t.transparency || [])), t
    };
    (0, r.useEffect)(() => (y(), N.current = setInterval(async () => {
      let e = await y();
      e.ok && !["pending_payment", "paid", "routing"].includes(e.order.status) && (N.current && clearInterval(N.current), l())
    }, 2500), () => {
      N.current && clearInterval(N.current)
    }), [e]);
    let z = async () => {
      await m("/api/store/payments/confirm", {
        publicId: e,
        ref: `${c?.rail}-${e}`
      }), await y()
    }, w = async () => {
      let t = await m(`/api/store/orders/${e}/restock`, {});
      t.ok && f(`تم التسجيل ✓ — ${t.waitingAhead} شخصًا قبلك في القائمة، سننبهك عند التوفير`)
    }, k = c ? [{
      key: "pending_payment",
      label: "بانتظار الدفع",
      done: !["pending_payment"].includes(c.status)
    }, {
      key: "paid",
      label: "تم الدفع",
      done: ["routing", "delivered", "failed"].includes(c.status)
    }, {
      key: "routing",
      label: "الموجّه يشتري",
      done: ["delivered", "failed"].includes(c.status)
    }, {
      key: "final",
      label: "failed" === c.status ? "استرداد كامل" : "تم التسليم",
      done: ["delivered", "failed"].includes(c.status)
    }] : [];
    return (0, t.jsx)(n.Card, {
      className: "bg-zinc-900/60 border-emerald-900/50",
      children: (0, t.jsxs)(n.CardContent, {
        className: "p-4 space-y-3",
        children: [(0, t.jsxs)("div", {
          className: "flex items-center justify-between",
          children: [(0, t.jsxs)("div", {
            className: "text-sm font-bold text-zinc-100",
            children: ["📦 الطلب ", (0, t.jsx)("span", {
              className: "font-mono text-cyan-300",
              dir: "ltr",
              children: e
            })]
          }), (0, t.jsx)(d, {
            size: "sm",
            variant: "ghost",
            className: "text-xs text-zinc-500 h-8",
            onClick: i,
            children: "→ رجوع للمتجر"
          })]
        }), c && (0, t.jsxs)(t.Fragment, {
          children: [(0, t.jsxs)("div", {
            className: "flex flex-wrap items-center gap-2",
            children: [(0, t.jsx)(a.Badge, {
              variant: "outline",
              className: `text-[10.5px] ${v[c.status]}`,
              children: c.statusAr
            }), (0, t.jsx)("span", {
              className: "text-[11px] text-zinc-400",
              children: c.product
            }), (0, t.jsx)("span", {
              className: "text-[11px] font-mono text-emerald-400",
              dir: "ltr",
              children: "SAR" === c.currency ? `${c.priceLocked} ر.س` : `$${c.priceLocked}`
            }), (0, t.jsx)("span", {
              className: "text-[10px] text-zinc-600",
              dir: "ltr",
              children: c.phoneMasked
            })]
          }), (0, t.jsx)("div", {
            className: "flex items-center gap-1",
            children: k.map((e, r) => (0, t.jsxs)("div", {
              className: "flex-1",
              children: [(0, t.jsx)("div", {
                className: `h-1.5 rounded-full ${e.done?"bg-emerald-600":"bg-zinc-800"}`
              }), (0, t.jsx)("div", {
                className: `text-[9.5px] mt-1 text-center ${e.done?"text-emerald-400":"text-zinc-600"}`,
                children: e.label
              })]
            }, e.key))
          }), "pending_payment" === c.status && c.payAddress && (0, t.jsxs)("div", {
            className: "rounded border border-amber-800/60 bg-amber-950/30 p-3 space-y-2",
            children: [(0, t.jsxs)("div", {
              className: "text-[11px] text-zinc-300 leading-5",
              children: ["أرسل ", (0, t.jsxs)("span", {
                className: "font-mono text-emerald-300",
                dir: "ltr",
                children: ["$", c.payAmount?.toFixed(2)]
              }), " إلى:", (0, t.jsx)("div", {
                className: "font-mono text-cyan-300 text-[11px] break-all mt-1",
                dir: "ltr",
                children: c.payAddress
              })]
            }), (0, t.jsx)(d, {
              className: "w-full h-10 text-xs bg-amber-800 hover:bg-amber-700 text-amber-50",
              onClick: z,
              children: "▶️ محاكاة تأكيد الدفع (sandbox) — يطلق الموجّه فورًا"
            })]
          }), "delivered" === c.status && c.deliveredPayload && (0, t.jsxs)("div", {
            className: "rounded border border-emerald-700 bg-emerald-950/40 p-3 space-y-2",
            children: [(0, t.jsxs)("div", {
              className: "text-[12px] font-bold text-emerald-300",
              children: ["🎉 تم التسليم عبر ", "ps" === c.winner ? "ProdSeller (شراء آلي)" : "sv" === c.winner ? "StackVault" : "Turgame"]
            }), (0, t.jsx)("button", {
              onClick: () => {
                c?.deliveredPayload && (navigator.clipboard?.writeText(c.deliveredPayload), b(!0), setTimeout(() => b(!1), 1800))
              },
              className: "w-full text-right rounded border border-emerald-800 bg-zinc-950 px-3 py-2.5 font-mono text-[12px] text-emerald-200 break-all hover:border-emerald-600",
              dir: "ltr",
              children: c.deliveredPayload
            }), (0, t.jsxs)("div", {
              className: "text-[10px] text-zinc-500",
              children: [h ? "✓ نُسخ" : "اضغط للنسخ", " · محفوظ في سجل طلبك دائمًا"]
            }), c.cashback > 0 && (0, t.jsxs)("div", {
              className: "text-[10.5px] text-amber-300",
              children: ["🪙 كاش باك 1% = ", (0, t.jsxs)("span", {
                className: "font-mono",
                dir: "ltr",
                children: ["$", c.cashback.toFixed(2)]
              }), " أُضيف لمحفظتك"]
            })]
          }), "failed" === c.status && (0, t.jsxs)("div", {
            className: "rounded border border-rose-800 bg-rose-950/40 p-3 space-y-2",
            children: [(0, t.jsx)("div", {
              className: "text-[12px] font-bold text-rose-300",
              children: "تعذّر التنفيذ من كل الموردين — المبلغ استُرد كاملًا لمحفظتك"
            }), (0, t.jsxs)("div", {
              className: "text-[10.5px] text-zinc-300 leading-5",
              children: ["💵 استرداد ", (0, t.jsxs)("span", {
                className: "font-mono text-emerald-300",
                dir: "ltr",
                children: ["$", c.amountUsd.toFixed(2)]
              }), " + 🎁 رصيد اعتذار ", (0, t.jsx)("span", {
                className: "font-mono text-emerald-300",
                dir: "ltr",
                children: "$1.00"
              })]
            }), p ? (0, t.jsx)("div", {
              className: "text-[10.5px] text-emerald-300",
              children: p
            }) : (0, t.jsx)(d, {
              size: "sm",
              className: "h-9 text-[11px] bg-zinc-800 hover:bg-zinc-700 text-zinc-200",
              onClick: w,
              children: "🔔 أعلمني عند التوفير"
            })]
          }), ["paid", "routing"].includes(c.status) && (0, t.jsx)("div", {
            className: "rounded border border-violet-800/60 bg-violet-950/30 p-2.5 text-[11px] text-violet-300 animate-pulse",
            children: "⚙️ الموجّه يعمل الآن: يفحص السلسلة → حارس الهامش → حارس الرصيد الحي → الشراء… (تلقائي بالكامل)"
          }), (0, t.jsxs)("div", {
            className: "rounded border border-zinc-800 bg-zinc-950/70 p-2.5",
            children: [(0, t.jsx)("div", {
              className: "text-[11px] font-bold text-zinc-300 mb-1.5",
              children: "🔍 شفافية الموجّه — ما يحدث خلف الكواليس (حقيقي 100%)"
            }), 0 === x.length ? (0, t.jsx)("div", {
              className: "text-[10.5px] text-zinc-600",
              children: "لا محاولات بعد…"
            }) : (0, t.jsx)("div", {
              className: "space-y-1 max-h-64 overflow-y-auto",
              children: x.map((e, r) => (0, t.jsxs)("div", {
                className: "flex items-start gap-2 text-[10.5px] leading-5",
                children: [(0, t.jsx)("span", {
                  children: g[e.status] ?? "•"
                }), (0, t.jsxs)("div", {
                  className: "flex-1",
                  children: [(0, t.jsx)("span", {
                    className: "text-zinc-300 font-bold",
                    children: e.supplier
                  }), (0, t.jsxs)("span", {
                    className: "text-zinc-500",
                    children: [" — ", e.stepAr]
                  }), null != e.latencyMs && (0, t.jsxs)("span", {
                    className: "text-zinc-600 font-mono",
                    dir: "ltr",
                    children: [" (", e.latencyMs, "ms)"]
                  }), e.message && (0, t.jsx)("div", {
                    className: "text-zinc-600 text-[10px] leading-4",
                    children: e.message
                  })]
                })]
              }, r))
            })]
          })]
        })]
      })
    })
  }
  let N = {
    deposit: "text-emerald-400",
    purchase: "text-rose-300",
    refund: "text-emerald-300",
    cashback: "text-amber-300",
    apology: "text-amber-300"
  };

  function y({
    phone: e,
    onBalance: i
  }) {
    let [l, c] = (0, r.useState)(0), [o, x] = (0, r.useState)([]), [u, p] = (0, r.useState)("25"), [f, h] = (0, r.useState)(!1), [b, g] = (0, r.useState)(null), v = (0, r.useCallback)(async () => {
      let t = await m(`/api/wallet?phone=${encodeURIComponent(e)}`);
      t.ok && (c(t.balance), x(t.txs), i(t.balance))
    }, [e, i]);
    (0, r.useEffect)(() => {
      v()
    }, [v]);
    let j = async () => {
      let t = Number(u);
      if (!(t >= 5) || t > 500) return void g("الإيداع بين $5 و$500");
      h(!0), g(null);
      let r = await m("/api/wallet/deposit", {
        phone: e,
        amountUsd: t
      });
      h(!1), g(r.ok ? `✓ ${r.note}` : r.error || "فشل"), await v()
    };
    return (0, t.jsx)(n.Card, {
      className: "bg-zinc-900/60 border-amber-900/50",
      children: (0, t.jsxs)(n.CardContent, {
        className: "p-4 space-y-3",
        children: [(0, t.jsxs)("div", {
          className: "flex flex-wrap items-center justify-between gap-2",
          children: [(0, t.jsx)("div", {
            className: "text-sm font-bold text-zinc-100",
            children: "👛 محفظتك — رصيد شرائي بالدولار"
          }), (0, t.jsxs)("div", {
            className: "text-2xl font-mono font-bold text-emerald-400",
            dir: "ltr",
            children: ["$", l.toFixed(2)]
          })]
        }), (0, t.jsxs)("div", {
          className: "rounded border border-amber-900/50 bg-amber-950/20 p-2.5 space-y-2",
          children: [(0, t.jsx)("div", {
            className: "text-[11px] font-bold text-amber-300",
            children: "إيداع (USDT TRC-20 / Binance Pay)"
          }), (0, t.jsxs)("div", {
            className: "flex gap-2",
            children: [(0, t.jsx)(s.Input, {
              dir: "ltr",
              type: "number",
              min: "5",
              max: "500",
              className: "flex-1 h-10 font-mono bg-zinc-950 border-zinc-700",
              value: u,
              onChange: e => p(e.target.value)
            }), (0, t.jsx)(d, {
              className: "h-10 bg-amber-800 hover:bg-amber-700 text-amber-50",
              disabled: f,
              onClick: j,
              children: f ? "⏳" : "إيداع"
            })]
          }), (0, t.jsx)("div", {
            className: "flex gap-1.5",
            children: [10, 25, 50, 100].map(e => (0, t.jsxs)("button", {
              onClick: () => p(String(e)),
              className: "text-[10px] rounded border border-zinc-700 bg-zinc-950 px-2 py-1 text-zinc-400 hover:border-amber-700",
              dir: "ltr",
              children: ["$", e]
            }, e))
          }), (0, t.jsx)("div", {
            className: "text-[9.5px] text-zinc-500 leading-4",
            children: "🧪 الوضع التجريبي: إيداع فوري موسوم. في الوضع الحي: عنوان إيداع مخصص + تأكيد on-chain ببلوك واحد. حدود W1: $5–$500. الرصيد للاستخدام الشرائي — استرداد نقدي كامل عند الطلب خلال 24 ساعة."
          }), b && (0, t.jsx)("div", {
            className: "text-[10.5px] text-emerald-300",
            children: b
          })]
        }), (0, t.jsxs)("div", {
          className: "rounded border border-zinc-800 bg-zinc-950/70 p-2.5",
          children: [(0, t.jsx)("div", {
            className: "text-[11px] font-bold text-zinc-300 mb-1.5",
            children: "📓 سجل الحركات (قيد مزدوج — الرصيد مشتق من السجل)"
          }), 0 === o.length ? (0, t.jsx)("div", {
            className: "text-[10.5px] text-zinc-600",
            children: "لا حركات بعد"
          }) : (0, t.jsx)("div", {
            className: "space-y-1 max-h-60 overflow-y-auto",
            children: o.map((e, r) => (0, t.jsxs)("div", {
              className: "flex items-center justify-between gap-2 text-[10.5px] border-b border-zinc-900 pb-1",
              children: [(0, t.jsxs)("div", {
                className: "flex items-center gap-2",
                children: [(0, t.jsx)(a.Badge, {
                  variant: "outline",
                  className: "text-[8.5px] border-zinc-700 text-zinc-400",
                  children: e.typeAr
                }), (0, t.jsx)("span", {
                  className: "text-zinc-600 text-[9.5px]",
                  children: new Date(e.at).toLocaleString("ar", {
                    hour: "2-digit",
                    minute: "2-digit",
                    month: "numeric",
                    day: "numeric"
                  })
                })]
              }), (0, t.jsxs)("span", {
                className: `font-mono ${N[e.type]??"text-zinc-300"}`,
                dir: "ltr",
                children: [e.amount > 0 ? "+" : "", "$", e.amount.toFixed(2)]
              })]
            }, r))
          })]
        })]
      })
    })
  }
  let z = {
    delivered: "text-emerald-400",
    failed: "text-rose-400",
    pending_payment: "text-amber-400",
    paid: "text-cyan-400",
    routing: "text-violet-400",
    refunded: "text-zinc-400"
  };

  function w({
    onSyncDone: e
  }) {
    let [s, i] = (0, r.useState)(null), [l, c] = (0, r.useState)(!1), [o, x] = (0, r.useState)(null), u = (0, r.useCallback)(async () => {
      let e = await m("/api/admin/stats");
      e.ok && i(e)
    }, []);
    (0, r.useEffect)(() => {
      u()
    }, [u]);
    let p = async () => {
      c(!0), x(null);
      let t = await m("/api/admin/sync", {});
      c(!1), t.ok ? (x(`✓ مزامنة حية: ${t.productsSeen} منتجًا في كتالوج ProdSeller \xb7 مطابقة ${t.matched} \xb7 تغيّر ${t.changed} \xb7 متوفر الآن ${t.inStockNow} \xb7 رصيد $${(t.balanceUsd??0).toFixed(2)} (${t.membership}) — ${t.latencyMs}ms`), e(), await u()) : x(`✗ ${t.error}`)
    };
    return (0, t.jsx)(n.Card, {
      className: "bg-zinc-900/60 border-cyan-900/50",
      children: (0, t.jsxs)(n.CardContent, {
        className: "p-4 space-y-3",
        children: [(0, t.jsxs)("div", {
          className: "flex flex-wrap items-center justify-between gap-2",
          children: [(0, t.jsx)("div", {
            className: "text-sm font-bold text-zinc-100",
            children: "🛠️ لوحة التشغيل — الموجّه والموردون والمزامنة"
          }), (0, t.jsx)(a.Badge, {
            variant: "outline",
            className: `text-[10px] font-mono ${s?.mode==="live"?"border-rose-700 text-rose-300":"border-amber-700 text-amber-300"}`,
            children: s?.mode === "live" ? "LIVE" : "SANDBOX"
          })]
        }), (0, t.jsxs)("div", {
          className: "grid grid-cols-2 sm:grid-cols-4 gap-2",
          children: [(0, t.jsxs)("div", {
            className: "rounded border border-zinc-800 bg-zinc-950/70 p-2.5 text-center",
            children: [(0, t.jsx)("div", {
              className: "text-[9.5px] text-zinc-500",
              children: "رصيد ProdSeller (حي)"
            }), (0, t.jsxs)("div", {
              className: "text-lg font-mono font-bold text-emerald-400",
              dir: "ltr",
              children: ["$", (s?.ps?.balanceUsd ?? 0).toFixed(2)]
            }), (0, t.jsxs)("div", {
              className: "text-[9px] text-zinc-600",
              children: [s?.ps?.username ?? "—", " · ", s?.ps?.membership ?? "—"]
            })]
          }), (0, t.jsxs)("div", {
            className: "rounded border border-zinc-800 bg-zinc-950/70 p-2.5 text-center",
            children: [(0, t.jsx)("div", {
              className: "text-[9.5px] text-zinc-500",
              children: "إجمالي الطلبات"
            }), (0, t.jsx)("div", {
              className: "text-lg font-mono font-bold text-cyan-300",
              dir: "ltr",
              children: s?.orders?.total ?? 0
            })]
          }), (0, t.jsxs)("div", {
            className: "rounded border border-zinc-800 bg-zinc-950/70 p-2.5 text-center",
            children: [(0, t.jsx)("div", {
              className: "text-[9.5px] text-zinc-500",
              children: "قائمة «أعلمني»"
            }), (0, t.jsx)("div", {
              className: "text-lg font-mono font-bold text-amber-300",
              dir: "ltr",
              children: s?.waitlistTotal ?? 0
            })]
          }), (0, t.jsxs)("div", {
            className: "rounded border border-zinc-800 bg-zinc-950/70 p-2.5 text-center",
            children: [(0, t.jsx)("div", {
              className: "text-[9.5px] text-zinc-500",
              children: "وضع المتجر"
            }), (0, t.jsx)("div", {
              className: "text-lg font-bold text-zinc-200",
              children: s?.mode === "live" ? "🔴 حي" : "🧪 تجريبي"
            })]
          })]
        }), (0, t.jsx)(d, {
          className: "w-full h-11 text-xs font-bold bg-cyan-900 hover:bg-cyan-800 text-cyan-50",
          disabled: l,
          onClick: p,
          children: l ? "⏳ جارٍ السحب الحي من ProdSeller…" : "🔄 مزامنة حية الآن — GET /v1/products + /v1/balance (تحديث الأسعار والمخزون)"
        }), o && (0, t.jsx)("div", {
          className: "text-[10.5px] text-zinc-300 bg-zinc-950/70 border border-zinc-800 rounded px-2.5 py-1.5 leading-5",
          children: o
        }), (0, t.jsxs)("div", {
          className: "rounded border border-zinc-800 bg-zinc-950/70 p-2.5",
          children: [(0, t.jsx)("div", {
            className: "text-[11px] font-bold text-zinc-300 mb-1.5",
            children: "🏆 درجات الموردين وقواطع الدائرة"
          }), (0, t.jsx)("div", {
            className: "overflow-x-auto",
            children: (0, t.jsxs)("table", {
              className: "w-full text-[10.5px]",
              children: [(0, t.jsx)("thead", {
                children: (0, t.jsxs)("tr", {
                  className: "text-zinc-500 border-b border-zinc-800 text-right",
                  children: [(0, t.jsx)("th", {
                    className: "p-1.5",
                    children: "المورد"
                  }), (0, t.jsx)("th", {
                    className: "p-1.5",
                    children: "النوع"
                  }), (0, t.jsx)("th", {
                    className: "p-1.5",
                    children: "درجة"
                  }), (0, t.jsx)("th", {
                    className: "p-1.5",
                    children: "إخفاقات"
                  }), (0, t.jsx)("th", {
                    className: "p-1.5",
                    children: "قاطع الدائرة"
                  }), (0, t.jsx)("th", {
                    className: "p-1.5",
                    children: "منتجات بالسلسلة"
                  })]
                })
              }), (0, t.jsx)("tbody", {
                children: (s?.suppliers ?? []).map((e, r) => (0, t.jsxs)("tr", {
                  className: `border-b border-zinc-900 ${e.active?"":"opacity-50"}`,
                  children: [(0, t.jsx)("td", {
                    className: "p-1.5 text-zinc-200 font-bold",
                    children: e.name
                  }), (0, t.jsx)("td", {
                    className: "p-1.5 text-zinc-500",
                    children: e.kind
                  }), (0, t.jsxs)("td", {
                    className: "p-1.5 font-mono text-cyan-300",
                    dir: "ltr",
                    children: [(100 * e.score).toFixed(0), "/100"]
                  }), (0, t.jsx)("td", {
                    className: "p-1.5 font-mono text-zinc-400",
                    dir: "ltr",
                    children: e.failCount
                  }), (0, t.jsx)("td", {
                    className: "p-1.5",
                    children: e.circuitOpen ? (0, t.jsx)("span", {
                      className: "text-rose-400 font-bold",
                      children: "مفتوح ⛔"
                    }) : (0, t.jsx)("span", {
                      className: "text-emerald-500",
                      children: "سليم ✓"
                    })
                  }), (0, t.jsx)("td", {
                    className: "p-1.5 font-mono text-zinc-400",
                    dir: "ltr",
                    children: e.chainCount
                  })]
                }, r))
              })]
            })
          })]
        }), (0, t.jsxs)("div", {
          className: "rounded border border-zinc-800 bg-zinc-950/70 p-2.5",
          children: [(0, t.jsx)("div", {
            className: "text-[11px] font-bold text-zinc-300 mb-1.5",
            children: "📋 أحدث الطلبات"
          }), 0 === (s?.orders?.recent ?? []).length ? (0, t.jsx)("div", {
            className: "text-[10.5px] text-zinc-600",
            children: "لا طلبات بعد — أنشئ طلبًا تجريبيًا من المتجر"
          }) : (0, t.jsx)("div", {
            className: "space-y-1 max-h-56 overflow-y-auto",
            children: (s.orders.recent ?? []).map((e, r) => (0, t.jsxs)("div", {
              className: "flex flex-wrap items-center justify-between gap-2 text-[10.5px] border-b border-zinc-900 pb-1",
              children: [(0, t.jsxs)("div", {
                className: "flex items-center gap-2",
                children: [(0, t.jsx)("span", {
                  className: "font-mono text-cyan-300",
                  dir: "ltr",
                  children: e.publicId
                }), (0, t.jsx)("span", {
                  className: "text-zinc-400",
                  children: e.product.slice(0, 30)
                }), (0, t.jsx)("span", {
                  className: "text-zinc-600",
                  dir: "ltr",
                  children: e.phone
                })]
              }), (0, t.jsxs)("div", {
                className: "flex items-center gap-2",
                children: [(0, t.jsx)("span", {
                  className: "font-mono text-zinc-500",
                  dir: "ltr",
                  children: "SAR" === e.currency ? `${e.price} ر.س` : `$${e.price}`
                }), (0, t.jsx)("span", {
                  className: `font-bold ${z[e.status]??"text-zinc-400"}`,
                  children: e.status
                }), e.winner && (0, t.jsx)(a.Badge, {
                  variant: "outline",
                  className: "text-[8.5px] border-emerald-800 text-emerald-400",
                  children: e.winner
                })]
              })]
            }, r))
          })]
        }), (0, t.jsxs)("div", {
          className: "rounded border border-zinc-800 bg-zinc-950/70 p-2.5",
          children: [(0, t.jsx)("div", {
            className: "text-[11px] font-bold text-zinc-300 mb-1.5",
            children: "🗂️ سجل المزامنة"
          }), 0 === (s?.syncs ?? []).length ? (0, t.jsx)("div", {
            className: "text-[10.5px] text-zinc-600",
            children: "لم تُنفّذ مزامنة بعد — اضغط زر المزامنة الحية"
          }) : (0, t.jsx)("div", {
            className: "space-y-1",
            children: (s.syncs ?? []).map((e, r) => (0, t.jsxs)("div", {
              className: `text-[10px] leading-4 ${e.ok?"text-zinc-400":"text-rose-400"}`,
              children: [e.ok ? "✓" : "✗", " ", e.message, " — ", new Date(e.at).toLocaleTimeString("ar")]
            }, r))
          })]
        })]
      })
    })
  }
  e.s(["Store", 0, function() {
    let e, [i, l] = (0, r.useState)(""),
      [c, o] = (0, r.useState)(""),
      [u, p] = (0, r.useState)("catalog"),
      [h, g] = (0, r.useState)(null),
      [v, N] = (0, r.useState)(null),
      [z, k] = (0, r.useState)(null),
      [S, C] = (0, r.useState)(null),
      [$, P] = (0, r.useState)(null),
      E = (e = i.replace(/\D/g, "")).startsWith("966") ? "SA" : e.startsWith("967") ? "YE" : "WW",
      _ = (0, r.useCallback)(async () => {
        let e = await m("/api/store/catalog");
        e.ok && g(e)
      }, []),
      T = (0, r.useCallback)(async () => {
        if (!i) return C(null);
        let e = await m(`/api/wallet?phone=${encodeURIComponent(i)}`);
        C(e.ok ? e.balance : null)
      }, [i]);
    (0, r.useEffect)(() => {
      let e = localStorage.getItem("mec-phone");
      e && (l(e), o(e)), _()
    }, [_]), (0, r.useEffect)(() => {
      i && T()
    }, [i, T, u]);
    let O = () => {
      let e = c.replace(/[^\d+]/g, "");
      e.replace(/\D/g, "").length < 8 ? P("أدخل رقم جوال صحيح مع رمز الدولة (مثال: +9665xxxxxxxx أو +9677xxxxxxxx)") : (l(e), localStorage.setItem("mec-phone", e), P(null), T())
    };
    return (0, t.jsxs)("div", {
      className: "space-y-4",
      children: [(0, t.jsx)(n.Card, {
        className: "bg-zinc-900/60 border-emerald-900/50",
        children: (0, t.jsxs)(n.CardContent, {
          className: "p-3 space-y-2.5",
          children: [(0, t.jsxs)("div", {
            className: "flex flex-wrap items-center gap-2 justify-between",
            children: [(0, t.jsxs)("div", {
              className: "flex items-center gap-2",
              children: [(0, t.jsx)(a.Badge, {
                variant: "outline",
                className: "font-mono text-[10px] border-emerald-700 bg-emerald-950/60 text-emerald-300",
                children: "MEC STORE W1"
              }), (0, t.jsx)(a.Badge, {
                variant: "outline",
                className: `text-[10px] font-mono ${h?.mode==="live"?"border-rose-700 bg-rose-950/60 text-rose-300":"border-amber-700 bg-amber-950/60 text-amber-300"}`,
                children: h?.mode === "live" ? "🔴 وضع حي" : "🧪 وضع تجريبي"
              }), h?.lastSyncAt && (0, t.jsxs)("span", {
                className: "text-[10px] text-zinc-500",
                children: ["آخر مزامنة: ", new Date(h.lastSyncAt).toLocaleTimeString("ar")]
              })]
            }), (0, t.jsxs)("div", {
              className: "flex items-center gap-1.5",
              children: [(0, t.jsxs)(d, {
                size: "sm",
                variant: "outline",
                className: `text-xs h-9 ${"wallet"===u?"border-amber-600 text-amber-300":"border-zinc-700 text-zinc-400"}`,
                onClick: () => p("wallet" === u ? "catalog" : "wallet"),
                children: ["👛 المحفظة ", null != S && (0, t.jsxs)("span", {
                  className: "font-mono text-emerald-400",
                  dir: "ltr",
                  children: [" $", S.toFixed(2)]
                })]
              }), (0, t.jsx)(d, {
                size: "sm",
                variant: "outline",
                className: `text-xs h-9 ${"admin"===u?"border-cyan-600 text-cyan-300":"border-zinc-700 text-zinc-400"}`,
                onClick: () => p("admin" === u ? "catalog" : "admin"),
                children: "🛠️ التشغيل"
              })]
            })]
          }), (0, t.jsxs)("div", {
            className: "flex flex-wrap gap-2 items-center",
            children: [(0, t.jsx)(s.Input, {
              dir: "ltr",
              className: "flex-1 min-w-52 font-mono text-sm h-10 bg-zinc-950 border-zinc-700",
              placeholder: "+9665xxxxxxxx أو +9677xxxxxxxx",
              value: c,
              onChange: e => o(e.target.value),
              onKeyDown: e => "Enter" === e.key && O()
            }), (0, t.jsx)(d, {
              className: "h-10 bg-emerald-900 hover:bg-emerald-800 text-emerald-100",
              onClick: O,
              children: "تسجيل / تحديث"
            }), i && (0, t.jsx)(a.Badge, {
              variant: "outline",
              className: "text-[11px] border-cyan-800 bg-cyan-950/60 text-cyan-300 py-1.5 px-2.5",
              children: x[E]
            })]
          }), (0, t.jsxs)("div", {
            className: "text-[10.5px] text-zinc-500 leading-4",
            children: ["🆔 هويتك = رقم جوالك (بلا كلمات مرور): يحدد منطقتك السعرية ويربط محفظتك وقائمة تنبيهاتك.", !i && " أدخل جوالك لعرض أسعار منطقتك."]
          }), $ && (0, t.jsx)("div", {
            className: "text-[11px] text-rose-400 bg-rose-950/40 border border-rose-900/50 rounded px-2.5 py-1.5",
            children: $
          })]
        })
      }), "catalog" === u && h && (0, t.jsx)(f, {
        data: h,
        region: E,
        hasPhone: !!i,
        onBuy: e => {
          N(e), p("checkout")
        },
        onRefresh: _
      }), "checkout" === u && v && (0, t.jsx)(b, {
        product: v,
        phone: i,
        region: E,
        balance: S,
        onDone: e => {
          k(e), p("order"), T()
        },
        onCancel: () => p("catalog"),
        onNeedWallet: () => p("wallet")
      }), "order" === u && z && (0, t.jsx)(j, {
        publicId: z,
        phone: i,
        onBack: () => {
          p("catalog"), _()
        },
        onWalletRefresh: T
      }), "wallet" === u && i && (0, t.jsx)(y, {
        phone: i,
        onBalance: C
      }), "wallet" === u && !i && (0, t.jsx)(n.Card, {
        className: "bg-zinc-900/60 border-amber-900/50",
        children: (0, t.jsx)(n.CardContent, {
          className: "p-4 text-sm text-zinc-400",
          children: "سجّل رقم جوالك أولًا لفتح المحفظة 👆"
        })
      }), "admin" === u && (0, t.jsx)(w, {
        onSyncDone: _
      })]
    })
  }], 53948)
}, 15288, 87486, 93479, e => {
  "use strict";
  var t = e.i(43476),
    r = e.i(75157);
  e.s(["Card", 0, function({
    className: e,
    ...n
  }) {
    return (0, t.jsx)("div", {
      "data-slot": "card",
      className: (0, r.cn)("bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm", e),
      ...n
    })
  }, "CardContent", 0, function({
    className: e,
    ...n
  }) {
    return (0, t.jsx)("div", {
      "data-slot": "card-content",
      className: (0, r.cn)("px-6", e),
      ...n
    })
  }, "CardHeader", 0, function({
    className: e,
    ...n
  }) {
    return (0, t.jsx)("div", {
      "data-slot": "card-header",
      className: (0, r.cn)("@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-1.5 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6", e),
      ...n
    })
  }, "CardTitle", 0, function({
    className: e,
    ...n
  }) {
    return (0, t.jsx)("div", {
      "data-slot": "card-title",
      className: (0, r.cn)("leading-none font-semibold", e),
      ...n
    })
  }], 15288);
  var n = e.i(91918);
  let a = (0, e.i(25913).cva)("inline-flex items-center justify-center rounded-md border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden", {
    variants: {
      variant: {
        default: "border-transparent bg-primary text-primary-foreground [a&]:hover:bg-primary/90",
        secondary: "border-transparent bg-secondary text-secondary-foreground [a&]:hover:bg-secondary/90",
        destructive: "border-transparent bg-destructive text-white [a&]:hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
        outline: "text-foreground [a&]:hover:bg-accent [a&]:hover:text-accent-foreground"
      }
    },
    defaultVariants: {
      variant: "default"
    }
  });
  e.s(["Badge", 0, function({
    className: e,
    variant: s,
    asChild: i = !1,
    ...l
  }) {
    let c = i ? n.Slot : "span";
    return (0, t.jsx)(c, {
      "data-slot": "badge",
      className: (0, r.cn)(a({
        variant: s
      }), e),
      ...l
    })
  }], 87486), e.s(["Input", 0, function({
    className: e,
    type: n,
    ...a
  }) {
    return (0, t.jsx)("input", {
      type: n,
      "data-slot": "input",
      className: (0, r.cn)("file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input flex h-9 w-full min-w-0 rounded-md border bg-transparent px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm", "focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]", "aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive", e),
      ...a
    })
  }], 93479)
}]);