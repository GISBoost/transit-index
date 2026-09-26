/* @ds-bundle: {"format":4,"namespace":"TransitIndexDesignSystem_923c60","components":[{"name":"LogoGeometry","sourcePath":"components/brand/Logo.jsx"},{"name":"Logo","sourcePath":"components/brand/Logo.jsx"},{"name":"Button","sourcePath":"components/core/Button.jsx"},{"name":"Card","sourcePath":"components/core/Card.jsx"},{"name":"Icon","sourcePath":"components/core/Icon.jsx"},{"name":"IconButton","sourcePath":"components/core/IconButton.jsx"},{"name":"Tag","sourcePath":"components/core/Tag.jsx"},{"name":"RankingBar","sourcePath":"components/data/RankingBar.jsx"},{"name":"SpeedLegend","sourcePath":"components/data/SpeedLegend.jsx"},{"name":"Stat","sourcePath":"components/data/Stat.jsx"},{"name":"Dialog","sourcePath":"components/feedback/Dialog.jsx"},{"name":"Toast","sourcePath":"components/feedback/Toast.jsx"},{"name":"Tooltip","sourcePath":"components/feedback/Tooltip.jsx"},{"name":"Checkbox","sourcePath":"components/forms/Checkbox.jsx"},{"name":"Input","sourcePath":"components/forms/Input.jsx"},{"name":"Radio","sourcePath":"components/forms/Radio.jsx"},{"name":"Select","sourcePath":"components/forms/Select.jsx"},{"name":"Switch","sourcePath":"components/forms/Switch.jsx"},{"name":"Tabs","sourcePath":"components/navigation/Tabs.jsx"},{"name":"LINES","sourcePath":"components/transit/LineBullet.jsx"},{"name":"LineBullet","sourcePath":"components/transit/LineBullet.jsx"},{"name":"TransitGeometry","sourcePath":"components/transit/LineBundle.jsx"},{"name":"LineBundle","sourcePath":"components/transit/LineBundle.jsx"},{"name":"LineSwatch","sourcePath":"components/transit/LineSwatch.jsx"},{"name":"RouteStrip","sourcePath":"components/transit/RouteStrip.jsx"},{"name":"SignArrow","sourcePath":"components/transit/SignArrow.jsx"},{"name":"StationSign","sourcePath":"components/transit/StationSign.jsx"}],"sourceHashes":{"components/brand/Logo.jsx":"94721e501863","components/core/Button.jsx":"f91bce5a2e2b","components/core/Card.jsx":"c68c90164a46","components/core/Icon.jsx":"76346a058485","components/core/IconButton.jsx":"d2347358b76f","components/core/Tag.jsx":"a6a51f89f32f","components/data/RankingBar.jsx":"1dee1a562a3f","components/data/SpeedLegend.jsx":"d653cdb1b025","components/data/Stat.jsx":"ec7b1fe9bcf8","components/feedback/Dialog.jsx":"61d3198f716e","components/feedback/Toast.jsx":"83f960b3f49d","components/feedback/Tooltip.jsx":"842866e4d8bb","components/forms/Checkbox.jsx":"e7f3a6896670","components/forms/Input.jsx":"a0918659975f","components/forms/Radio.jsx":"61230a57eb31","components/forms/Select.jsx":"8f68f53474a1","components/forms/Switch.jsx":"1b8f43e33b83","components/navigation/Tabs.jsx":"64389de55ee6","components/transit/LineBullet.jsx":"3e008b4da983","components/transit/LineBundle.jsx":"83cd8fd0be90","components/transit/LineSwatch.jsx":"790c993dd36a","components/transit/RouteStrip.jsx":"ae4ba27850c1","components/transit/SignArrow.jsx":"2d7bd8a367d4","components/transit/StationSign.jsx":"b2faa8e8b343","ui_kits/landing/Sections.jsx":"0ef532f5b725","ui_kits/landing/copy.js":"2d6f23439b9d","ui_kits/landing/journey.js":"55180b33bfda"},"inlinedExternals":[],"unexposedExports":[{"name":"resolveLine","sourcePath":"components/transit/LineBullet.jsx"}]} */

(() => {

const __ds_ns = (window.TransitIndexDesignSystem_923c60 = window.TransitIndexDesignSystem_923c60 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/core/Card.jsx
try { (() => {
const SURF = {
  white: {
    bg: 'var(--white)',
    fg: 'var(--ink)',
    bd: 'var(--border-w) solid var(--ink)',
    r: 'var(--radius-0)',
    rule: 'var(--ink)'
  },
  paper: {
    bg: 'var(--paper-2)',
    fg: 'var(--ink)',
    bd: 'none',
    r: 'var(--radius-0)',
    rule: 'var(--ink)'
  },
  outline: {
    bg: 'transparent',
    fg: 'var(--ink)',
    bd: 'var(--border-w) solid var(--ink)',
    r: 'var(--radius-0)',
    rule: 'var(--ink)'
  },
  sign: {
    bg: 'var(--ink)',
    fg: 'var(--paper)',
    bd: 'none',
    r: 'var(--radius-sign)',
    rule: 'var(--paper)'
  },
  red: {
    bg: 'var(--poster-red)',
    fg: '#fff',
    bd: 'none',
    r: 'var(--radius-0)',
    rule: 'var(--ink)'
  },
  petrol: {
    bg: 'var(--poster-petrol)',
    fg: '#fff',
    bd: 'none',
    r: 'var(--radius-0)',
    rule: 'var(--ink)'
  },
  mustard: {
    bg: 'var(--poster-mustard)',
    fg: 'var(--ink)',
    bd: 'none',
    r: 'var(--radius-0)',
    rule: 'var(--ink)'
  }
};
function Card({
  children,
  surface = 'white',
  rule = false,
  padding = 24,
  onClick,
  style
}) {
  const s = SURF[surface] || SURF.white;
  return /*#__PURE__*/React.createElement("div", {
    onClick: onClick,
    style: {
      background: s.bg,
      color: s.fg,
      border: s.bd,
      borderTop: rule ? 'var(--rule-w) solid ' + s.rule : undefined,
      borderRadius: s.r,
      padding,
      boxSizing: 'border-box',
      cursor: onClick ? 'pointer' : undefined,
      fontFamily: 'var(--font-sans)',
      ...style
    }
  }, children);
}
Object.assign(__ds_scope, { Card });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Card.jsx", error: String((e && e.message) || e) }); }

// components/core/Icon.jsx
try { (() => {
function Icon({
  name,
  size = 24,
  fill = 1,
  weight = 700,
  color,
  title,
  style
}) {
  const opsz = Math.min(48, Math.max(20, size));
  return /*#__PURE__*/React.createElement("span", {
    role: title ? 'img' : undefined,
    "aria-label": title,
    "aria-hidden": title ? undefined : 'true',
    style: {
      fontFamily: "'Material Symbols Sharp'",
      fontWeight: 'normal',
      fontStyle: 'normal',
      fontSize: size,
      lineHeight: 1,
      width: size,
      height: size,
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      overflow: 'hidden',
      letterSpacing: 'normal',
      textTransform: 'none',
      whiteSpace: 'nowrap',
      direction: 'ltr',
      fontFeatureSettings: "'liga'",
      WebkitFontSmoothing: 'antialiased',
      fontVariationSettings: "'FILL' " + fill + ", 'wght' " + weight + ", 'GRAD' 0, 'opsz' " + opsz,
      color: color || 'currentColor',
      flexShrink: 0,
      userSelect: 'none',
      ...style
    }
  }, name);
}
Object.assign(__ds_scope, { Icon });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Icon.jsx", error: String((e && e.message) || e) }); }

// components/core/Button.jsx
try { (() => {
const {
  useState
} = React;
const SIZES = {
  sm: {
    h: 32,
    px: 12,
    fs: 13,
    ic: 16,
    gap: 6
  },
  md: {
    h: 44,
    px: 18,
    fs: 15,
    ic: 20,
    gap: 8
  },
  lg: {
    h: 56,
    px: 24,
    fs: 18,
    ic: 24,
    gap: 10
  }
};
const VARIANTS = {
  primary: {
    bg: 'var(--ink)',
    fg: 'var(--paper)',
    bd: 'var(--ink)',
    hbg: 'var(--ink-2)',
    hfg: 'var(--paper)',
    hbd: 'var(--ink-2)'
  },
  accent: {
    bg: 'var(--poster-red)',
    fg: '#fff',
    bd: 'var(--poster-red)',
    hbg: 'var(--poster-red-dark)',
    hfg: '#fff',
    hbd: 'var(--poster-red-dark)'
  },
  secondary: {
    bg: 'transparent',
    fg: 'var(--ink)',
    bd: 'var(--ink)',
    hbg: 'var(--ink)',
    hfg: 'var(--paper)',
    hbd: 'var(--ink)'
  },
  ghost: {
    bg: 'transparent',
    fg: 'var(--ink)',
    bd: 'transparent',
    hbg: 'var(--paper-2)',
    hfg: 'var(--ink)',
    hbd: 'transparent'
  },
  inverse: {
    bg: 'var(--paper)',
    fg: 'var(--ink)',
    bd: 'var(--paper)',
    hbg: '#fff',
    hfg: 'var(--ink)',
    hbd: '#fff'
  }
};
function Button({
  children,
  variant = 'primary',
  size = 'md',
  iconLeft,
  iconRight,
  disabled = false,
  fullWidth = false,
  type = 'button',
  onClick,
  style
}) {
  const [hover, setHover] = useState(false);
  const [down, setDown] = useState(false);
  const s = SIZES[size] || SIZES.md;
  const v = VARIANTS[variant] || VARIANTS.primary;
  const h = hover && !disabled;
  return /*#__PURE__*/React.createElement("button", {
    type: type,
    disabled: disabled,
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => {
      setHover(false);
      setDown(false);
    },
    onMouseDown: () => setDown(true),
    onMouseUp: () => setDown(false),
    style: {
      display: fullWidth ? 'flex' : 'inline-flex',
      width: fullWidth ? '100%' : undefined,
      alignItems: 'center',
      justifyContent: 'center',
      gap: s.gap,
      height: s.h,
      padding: '0 ' + s.px + 'px',
      boxSizing: 'border-box',
      fontFamily: 'var(--font-sans)',
      fontSize: s.fs,
      fontWeight: 700,
      letterSpacing: '-0.005em',
      lineHeight: 1,
      background: h ? v.hbg : v.bg,
      color: h ? v.hfg : v.fg,
      border: 'var(--border-w) solid ' + (h ? v.hbd : v.bd),
      borderRadius: 'var(--radius-0)',
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.4 : 1,
      transform: down && !disabled ? 'translateY(1px)' : 'none',
      transition: 'background var(--dur-fast) var(--ease-transit), color var(--dur-fast) var(--ease-transit), border-color var(--dur-fast) var(--ease-transit)',
      whiteSpace: 'nowrap',
      ...style
    }
  }, iconLeft && /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: iconLeft,
    size: s.ic
  }), children, iconRight && /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: iconRight,
    size: s.ic
  }));
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Button.jsx", error: String((e && e.message) || e) }); }

// components/core/IconButton.jsx
try { (() => {
const {
  useState
} = React;
const SIZES = {
  sm: {
    d: 32,
    ic: 18
  },
  md: {
    d: 44,
    ic: 22
  },
  lg: {
    d: 56,
    ic: 28
  }
};
const VARIANTS = {
  primary: {
    bg: 'var(--ink)',
    fg: 'var(--paper)',
    bd: 'var(--ink)',
    hbg: 'var(--ink-2)',
    hfg: 'var(--paper)'
  },
  accent: {
    bg: 'var(--poster-red)',
    fg: '#fff',
    bd: 'var(--poster-red)',
    hbg: 'var(--poster-red-dark)',
    hfg: '#fff'
  },
  secondary: {
    bg: 'transparent',
    fg: 'var(--ink)',
    bd: 'var(--ink)',
    hbg: 'var(--ink)',
    hfg: 'var(--paper)'
  },
  ghost: {
    bg: 'transparent',
    fg: 'var(--ink)',
    bd: 'transparent',
    hbg: 'var(--paper-2)',
    hfg: 'var(--ink)'
  }
};
function IconButton({
  icon,
  label,
  variant = 'ghost',
  size = 'md',
  shape = 'square',
  disabled = false,
  onClick,
  style
}) {
  const [hover, setHover] = useState(false);
  const s = SIZES[size] || SIZES.md;
  const v = VARIANTS[variant] || VARIANTS.ghost;
  const h = hover && !disabled;
  return /*#__PURE__*/React.createElement("button", {
    type: "button",
    "aria-label": label,
    title: label,
    disabled: disabled,
    onClick: onClick,
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => setHover(false),
    style: {
      width: s.d,
      height: s.d,
      padding: 0,
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      boxSizing: 'border-box',
      background: h ? v.hbg : v.bg,
      color: h ? v.hfg : v.fg,
      border: 'var(--border-w) solid ' + (h && variant !== 'ghost' ? v.hbg : v.bd),
      borderRadius: shape === 'circle' ? '50%' : 'var(--radius-0)',
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.4 : 1,
      transition: 'background var(--dur-fast) var(--ease-transit), color var(--dur-fast) var(--ease-transit)',
      ...style
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: s.ic
  }));
}
Object.assign(__ds_scope, { IconButton });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/IconButton.jsx", error: String((e && e.message) || e) }); }

// components/data/RankingBar.jsx
try { (() => {
function RankingBar({
  rank,
  label,
  value,
  max = 25,
  unit = 'km/h',
  decimals = 1,
  locale = 'pl',
  flag,
  flagLabel,
  highlight = false,
  onClick,
  style
}) {
  const fmt = value == null ? '—' : Number(value).toLocaleString(locale === 'en' ? 'en-GB' : 'pl-PL', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
  const pct = value == null ? 0 : Math.max(0, Math.min(1, value / max)) * 100;
  const thin = flag === 'thin';
  const barBg = thin ? 'repeating-linear-gradient(135deg,var(--ink) 0 3px,transparent 3px 6px)' : highlight ? 'var(--accent)' : 'var(--ink)';
  return /*#__PURE__*/React.createElement("div", {
    onClick: onClick,
    style: {
      display: 'grid',
      gridTemplateColumns: '32px minmax(96px,160px) minmax(0,1fr) 88px',
      alignItems: 'center',
      gap: 12,
      padding: '8px 0',
      borderBottom: '1px solid var(--border-subtle)',
      fontFamily: 'var(--font-sans)',
      color: 'var(--ink)',
      cursor: onClick ? 'pointer' : undefined,
      ...style
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-condensed)',
      fontWeight: 700,
      fontSize: 15,
      fontVariantNumeric: 'tabular-nums',
      color: 'var(--ink-3)'
    }
  }, String(rank).padStart(2, '0')), /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 6,
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 700,
      fontSize: 17,
      letterSpacing: '-0.01em',
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    }
  }, label), flag && /*#__PURE__*/React.createElement("span", {
    title: flagLabel,
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 2,
      fontFamily: 'var(--font-condensed)',
      fontSize: 11,
      fontWeight: 700,
      textTransform: 'uppercase',
      letterSpacing: '.06em',
      color: 'var(--ink-3)',
      whiteSpace: 'nowrap'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: flag === 'thin' ? 'texture' : 'report',
    size: 14
  }), flagLabel)), /*#__PURE__*/React.createElement("span", {
    style: {
      height: 14,
      position: 'relative',
      background: 'transparent'
    }
  }, /*#__PURE__*/React.createElement("span", {
    "data-bar": "",
    style: {
      position: 'absolute',
      left: 0,
      top: 0,
      bottom: 0,
      width: pct + '%',
      background: barBg,
      outline: thin ? '2px solid var(--ink)' : 'none',
      outlineOffset: -2,
      transformOrigin: '0 50%'
    }
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      textAlign: 'right',
      fontVariantNumeric: 'tabular-nums',
      whiteSpace: 'nowrap'
    }
  }, /*#__PURE__*/React.createElement("b", {
    style: {
      fontSize: 18
    }
  }, fmt), " ", /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 12,
      color: 'var(--ink-3)'
    }
  }, unit)));
}
Object.assign(__ds_scope, { RankingBar });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/RankingBar.jsx", error: String((e && e.message) || e) }); }

// components/data/SpeedLegend.jsx
try { (() => {
function SpeedLegend({
  title = 'Prędkość',
  unit = 'km/h',
  labels = ['< 10', '10–14', '14–18', '18–22', '> 22'],
  slowLabel = 'wolniej',
  fastLabel = 'szybciej',
  noDataLabel = 'brak danych',
  thinLabel = 'mała próba',
  style
}) {
  const sw = {
    height: 8,
    width: '100%'
  };
  const lab = {
    fontFamily: 'var(--font-condensed)',
    fontSize: 13,
    lineHeight: 1.1,
    fontVariantNumeric: 'tabular-nums',
    whiteSpace: 'nowrap'
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-sans)',
      color: 'var(--ink)',
      display: 'flex',
      flexDirection: 'column',
      gap: 8,
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'baseline',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("b", {
    style: {
      fontSize: 13
    }
  }, title), /*#__PURE__*/React.createElement("span", {
    style: {
      ...lab,
      color: 'var(--ink-3)'
    }
  }, unit)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 16,
      alignItems: 'flex-start',
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(' + labels.length + ',minmax(44px,1fr))',
      gap: 3,
      flex: '1 1 240px'
    }
  }, labels.map((l, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 5
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...sw,
      background: 'var(--speed-' + (i + 1) + ')'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: lab
  }, l))), /*#__PURE__*/React.createElement("span", {
    style: {
      ...lab,
      gridColumn: '1 / span 2',
      color: 'var(--ink-3)'
    }
  }, "\u2190 ", slowLabel), /*#__PURE__*/React.createElement("span", {
    style: {
      ...lab,
      gridColumn: labels.length - 1 + ' / span 2',
      textAlign: 'right',
      color: 'var(--ink-3)'
    }
  }, fastLabel, " \u2192")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 5,
      width: 64
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...sw,
      background: 'var(--speed-nodata)'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: lab
  }, noDataLabel)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 5,
      width: 64
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      ...sw,
      background: 'repeating-linear-gradient(135deg,var(--speed-3) 0 3px,var(--map-base) 3px 6px)',
      outline: '1px solid var(--speed-3)',
      outlineOffset: -1
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: lab
  }, thinLabel)))));
}
Object.assign(__ds_scope, { SpeedLegend });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/SpeedLegend.jsx", error: String((e && e.message) || e) }); }

// components/data/Stat.jsx
try { (() => {
const SZ = {
  md: {
    v: 48,
    u: 18,
    l: 14
  },
  lg: {
    v: 96,
    u: 28,
    l: 16
  },
  xl: {
    v: 200,
    u: 44,
    l: 18
  }
};
function Stat({
  value,
  unit,
  label,
  size = 'lg',
  misregister = false,
  style
}) {
  const s = SZ[size] || SZ.lg;
  const num = {
    fontWeight: 700,
    fontSize: 'min(' + s.v + 'px, ' + s.v / 9.6 + 'vw + 24px)',
    lineHeight: .88,
    letterSpacing: '-0.045em',
    fontVariantNumeric: 'tabular-nums',
    whiteSpace: 'nowrap'
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-sans)',
      color: 'var(--ink)',
      display: 'flex',
      flexDirection: 'column',
      gap: 10,
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: Math.round(s.u * 0.4)
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'relative',
      display: 'inline-block'
    }
  }, misregister && /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      ...num,
      position: 'absolute',
      left: '0.035em',
      top: '0.03em',
      color: 'var(--poster-red)'
    }
  }, value), /*#__PURE__*/React.createElement("span", {
    style: {
      ...num,
      position: 'relative'
    }
  }, value)), unit && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: s.u,
      fontWeight: 700,
      letterSpacing: '-0.02em'
    }
  }, unit)), label && /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: s.l,
      lineHeight: 1.4,
      maxWidth: 420,
      textWrap: 'pretty'
    }
  }, label));
}
Object.assign(__ds_scope, { Stat });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/data/Stat.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Dialog.jsx
try { (() => {
const {
  useEffect
} = React;
function Dialog({
  open,
  onClose,
  title,
  children,
  actions,
  width = 520
}) {
  useEffect(() => {
    if (!open) return;
    const k = e => {
      if (e.key === 'Escape' && onClose) onClose();
    };
    window.addEventListener('keydown', k);
    return () => window.removeEventListener('keydown', k);
  }, [open, onClose]);
  if (!open) return null;
  return /*#__PURE__*/React.createElement("div", {
    onClick: onClose,
    style: {
      position: 'fixed',
      inset: 0,
      background: 'var(--scrim)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 24,
      zIndex: 1000
    }
  }, /*#__PURE__*/React.createElement("div", {
    role: "dialog",
    "aria-modal": "true",
    onClick: e => e.stopPropagation(),
    style: {
      width: '100%',
      maxWidth: width,
      background: 'var(--paper)',
      color: 'var(--ink)',
      border: 'var(--border-w) solid var(--ink)',
      borderTop: 'var(--rule-w) solid var(--ink)',
      fontFamily: 'var(--font-sans)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'space-between',
      gap: 16,
      padding: '20px 16px 12px 24px'
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: 0,
      fontSize: 26,
      fontWeight: 700,
      letterSpacing: '-0.02em',
      lineHeight: 1.1
    }
  }, title), onClose && /*#__PURE__*/React.createElement(__ds_scope.IconButton, {
    icon: "close",
    label: "Zamknij",
    onClick: onClose,
    size: "sm"
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: '0 24px 24px',
      fontSize: 16,
      lineHeight: 1.45
    }
  }, children), actions && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'flex-end',
      gap: 8,
      padding: '16px 24px',
      borderTop: 'var(--border-w) solid var(--ink)'
    }
  }, actions)));
}
Object.assign(__ds_scope, { Dialog });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Dialog.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Toast.jsx
try { (() => {
const TONES = {
  info: {
    bg: 'var(--line-blue)',
    fg: '#fff',
    ic: 'info'
  },
  success: {
    bg: 'var(--line-green)',
    fg: '#fff',
    ic: 'check'
  },
  warning: {
    bg: 'var(--line-yellow)',
    fg: 'var(--ink)',
    ic: 'warning'
  },
  danger: {
    bg: 'var(--poster-red)',
    fg: '#fff',
    ic: 'block'
  }
};
function Toast({
  tone = 'info',
  title,
  message,
  action,
  onClose,
  style
}) {
  const t = TONES[tone] || TONES.info;
  return /*#__PURE__*/React.createElement("div", {
    role: "status",
    style: {
      display: 'flex',
      alignItems: 'stretch',
      background: 'var(--ink)',
      color: 'var(--paper)',
      minWidth: 300,
      maxWidth: 460,
      fontFamily: 'var(--font-sans)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 52,
      flexShrink: 0,
      background: t.bg,
      color: t.fg,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: t.ic,
    size: 26
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      padding: '12px 14px',
      minWidth: 0
    }
  }, title && /*#__PURE__*/React.createElement("div", {
    style: {
      fontWeight: 700,
      fontSize: 15,
      lineHeight: 1.25
    }
  }, title), message && /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 14,
      lineHeight: 1.35,
      marginTop: title ? 2 : 0,
      color: 'var(--paper-2)'
    }
  }, message), action && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 8
    }
  }, action)), onClose && /*#__PURE__*/React.createElement("span", {
    style: {
      padding: 6,
      display: 'flex',
      alignItems: 'flex-start'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.IconButton, {
    icon: "close",
    label: "Zamknij",
    size: "sm",
    onClick: onClose,
    style: {
      color: 'var(--paper)'
    }
  })));
}
Object.assign(__ds_scope, { Toast });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Toast.jsx", error: String((e && e.message) || e) }); }

// components/feedback/Tooltip.jsx
try { (() => {
const {
  useState
} = React;
function Tooltip({
  content,
  children,
  placement = 'top'
}) {
  const [show, setShow] = useState(false);
  const top = placement === 'top';
  return /*#__PURE__*/React.createElement("span", {
    onMouseEnter: () => setShow(true),
    onMouseLeave: () => setShow(false),
    onFocus: () => setShow(true),
    onBlur: () => setShow(false),
    style: {
      position: 'relative',
      display: 'inline-flex'
    }
  }, children, show && /*#__PURE__*/React.createElement("span", {
    role: "tooltip",
    style: {
      position: 'absolute',
      left: '50%',
      transform: 'translateX(-50%)',
      [top ? 'bottom' : 'top']: 'calc(100% + 8px)',
      background: 'var(--ink)',
      color: 'var(--paper)',
      fontFamily: 'var(--font-sans)',
      fontSize: 13,
      fontWeight: 400,
      lineHeight: 1.2,
      padding: '6px 10px',
      whiteSpace: 'nowrap',
      zIndex: 50,
      pointerEvents: 'none'
    }
  }, content, /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      left: '50%',
      [top ? 'bottom' : 'top']: -4,
      width: 8,
      height: 8,
      background: 'var(--ink)',
      transform: 'translateX(-50%) rotate(45deg)'
    }
  })));
}
Object.assign(__ds_scope, { Tooltip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/Tooltip.jsx", error: String((e && e.message) || e) }); }

// components/forms/Checkbox.jsx
try { (() => {
const {
  useState
} = React;
function Checkbox({
  label,
  checked,
  defaultChecked = false,
  onChange,
  disabled = false,
  style
}) {
  const [inner, setInner] = useState(defaultChecked);
  const on = checked !== undefined ? checked : inner;
  const toggle = () => {
    if (disabled) return;
    const n = !on;
    if (checked === undefined) setInner(n);
    onChange && onChange(n);
  };
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 10,
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.45 : 1,
      fontFamily: 'var(--font-sans)',
      fontSize: 15,
      color: 'var(--ink)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("span", {
    role: "checkbox",
    "aria-checked": on,
    tabIndex: 0,
    onClick: toggle,
    onKeyDown: e => {
      if (e.key === ' ') {
        e.preventDefault();
        toggle();
      }
    },
    style: {
      width: 22,
      height: 22,
      boxSizing: 'border-box',
      border: 'var(--border-w) solid var(--ink)',
      background: on ? 'var(--ink)' : 'var(--white)',
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'var(--paper)',
      transition: 'background var(--dur-fast) var(--ease-transit)',
      flexShrink: 0
    }
  }, on && /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "check",
    size: 18
  })), label && /*#__PURE__*/React.createElement("span", {
    onClick: toggle
  }, label));
}
Object.assign(__ds_scope, { Checkbox });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Checkbox.jsx", error: String((e && e.message) || e) }); }

// components/forms/Input.jsx
try { (() => {
const {
  useState
} = React;
function Input({
  label,
  value,
  defaultValue,
  placeholder,
  onChange,
  hint,
  error,
  disabled = false,
  iconLeft,
  type = 'text',
  id,
  style
}) {
  const [focus, setFocus] = useState(false);
  const fid = id || (label ? 'in-' + String(label).replace(/\W+/g, '-').toLowerCase() : undefined);
  const bd = error ? 'var(--danger)' : focus ? 'var(--focus-ring)' : 'var(--ink)';
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 6,
      fontFamily: 'var(--font-sans)',
      opacity: disabled ? 0.45 : 1,
      ...style
    }
  }, label && /*#__PURE__*/React.createElement("label", {
    htmlFor: fid,
    style: {
      fontSize: 13,
      fontWeight: 700,
      color: 'var(--ink)'
    }
  }, label), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 8,
      height: 44,
      padding: '0 12px',
      boxSizing: 'border-box',
      background: 'var(--white)',
      border: 'var(--border-w) solid ' + bd,
      boxShadow: focus ? '0 0 0 2px ' + bd : 'none',
      transition: 'box-shadow var(--dur-fast) var(--ease-transit)'
    }
  }, iconLeft && /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: iconLeft,
    size: 20,
    color: "var(--ink-3)"
  }), /*#__PURE__*/React.createElement("input", {
    id: fid,
    type: type,
    value: value,
    defaultValue: defaultValue,
    placeholder: placeholder,
    disabled: disabled,
    onChange: onChange,
    onFocus: () => setFocus(true),
    onBlur: () => setFocus(false),
    style: {
      flex: 1,
      minWidth: 0,
      border: 0,
      outline: 0,
      background: 'transparent',
      fontFamily: 'inherit',
      fontSize: 16,
      color: 'var(--ink)',
      height: '100%',
      padding: 0
    }
  })), (error || hint) && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: 13,
      color: error ? 'var(--danger)' : 'var(--text-muted)'
    }
  }, error || hint));
}
Object.assign(__ds_scope, { Input });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Input.jsx", error: String((e && e.message) || e) }); }

// components/forms/Radio.jsx
try { (() => {
function Radio({
  label,
  checked = false,
  name,
  value,
  onChange,
  disabled = false,
  style
}) {
  const pick = () => {
    if (!disabled && onChange) onChange(value);
  };
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 10,
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.45 : 1,
      fontFamily: 'var(--font-sans)',
      fontSize: 15,
      color: 'var(--ink)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("input", {
    type: "radio",
    name: name,
    value: value,
    checked: checked,
    onChange: pick,
    disabled: disabled,
    style: {
      position: 'absolute',
      opacity: 0,
      width: 0,
      height: 0
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      width: 22,
      height: 22,
      borderRadius: '50%',
      boxSizing: 'border-box',
      border: '3px solid var(--ink)',
      background: 'var(--white)',
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexShrink: 0
    }
  }, checked && /*#__PURE__*/React.createElement("span", {
    style: {
      width: 10,
      height: 10,
      borderRadius: '50%',
      background: 'var(--ink)'
    }
  })), label && /*#__PURE__*/React.createElement("span", null, label));
}
Object.assign(__ds_scope, { Radio });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Radio.jsx", error: String((e && e.message) || e) }); }

// components/forms/Select.jsx
try { (() => {
const {
  useState
} = React;
function Select({
  label,
  options = [],
  value,
  defaultValue,
  onChange,
  disabled = false,
  id,
  style
}) {
  const [focus, setFocus] = useState(false);
  const fid = id || (label ? 'sel-' + String(label).replace(/\W+/g, '-').toLowerCase() : undefined);
  const bd = focus ? 'var(--focus-ring)' : 'var(--ink)';
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 6,
      fontFamily: 'var(--font-sans)',
      opacity: disabled ? 0.45 : 1,
      ...style
    }
  }, label && /*#__PURE__*/React.createElement("label", {
    htmlFor: fid,
    style: {
      fontSize: 13,
      fontWeight: 700
    }
  }, label), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement("select", {
    id: fid,
    value: value,
    defaultValue: defaultValue,
    onChange: onChange,
    disabled: disabled,
    onFocus: () => setFocus(true),
    onBlur: () => setFocus(false),
    style: {
      appearance: 'none',
      WebkitAppearance: 'none',
      width: '100%',
      height: 44,
      padding: '0 40px 0 12px',
      background: 'var(--white)',
      border: 'var(--border-w) solid ' + bd,
      boxShadow: focus ? '0 0 0 2px ' + bd : 'none',
      borderRadius: 0,
      fontFamily: 'inherit',
      fontSize: 16,
      color: 'var(--ink)',
      outline: 0,
      cursor: 'pointer'
    }
  }, options.map(o => {
    const v = typeof o === 'string' ? o : o.value;
    const l = typeof o === 'string' ? o : o.label;
    return /*#__PURE__*/React.createElement("option", {
      key: v,
      value: v
    }, l);
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      right: 10,
      top: 0,
      bottom: 0,
      display: 'flex',
      alignItems: 'center',
      pointerEvents: 'none'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: "expand_more",
    size: 22
  }))));
}
Object.assign(__ds_scope, { Select });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Select.jsx", error: String((e && e.message) || e) }); }

// components/transit/LineBullet.jsx
try { (() => {
const LINES = ['vermilion', 'orange', 'yellow', 'green', 'sky', 'blue', 'violet', 'black'];
const ALIAS = {
  red: 'vermilion',
  cyan: 'sky',
  ink: 'black'
};
const DARK = new Set(['yellow', 'orange', 'sky']);
function resolveLine(k) {
  if (!k) return {
    bg: 'var(--line-black)',
    fg: 'var(--paper)'
  };
  const key = ALIAS[k] || k;
  if (key === 'black') return {
    bg: 'var(--line-black)',
    fg: 'var(--paper)'
  };
  if (key === 'paper') return {
    bg: 'var(--paper)',
    fg: 'var(--ink)'
  };
  if (LINES.includes(key)) return {
    bg: 'var(--line-' + key + ')',
    fg: DARK.has(key) ? '#1E1D26' : '#fff'
  };
  return {
    bg: k,
    fg: '#fff'
  };
}
const SZ = {
  xs: 18,
  sm: 24,
  md: 36,
  lg: 56,
  xl: 96
};
function LineBullet({
  label,
  line = 'vermilion',
  size = 'md',
  shape = 'circle',
  textColor,
  style
}) {
  const d = typeof size === 'number' ? size : SZ[size] || 36;
  const c = resolveLine(line);
  const len = String(label ?? '').length;
  const fs = Math.round(d * (len > 2 ? 0.4 : len > 1 ? 0.5 : 0.62));
  const inner = /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--font-sans)',
      fontWeight: 700,
      fontSize: fs,
      lineHeight: 1,
      letterSpacing: '-0.02em',
      fontVariantNumeric: 'tabular-nums',
      color: textColor || c.fg,
      transform: shape === 'diamond' ? 'rotate(-45deg)' : undefined
    }
  }, label);
  return /*#__PURE__*/React.createElement("span", {
    style: {
      width: shape === 'diamond' ? d * 0.78 : d,
      height: shape === 'diamond' ? d * 0.78 : d,
      margin: shape === 'diamond' ? d * 0.11 : 0,
      borderRadius: shape === 'circle' ? '50%' : 'var(--radius-0)',
      transform: shape === 'diamond' ? 'rotate(45deg)' : undefined,
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: c.bg,
      flexShrink: 0,
      boxSizing: 'border-box',
      ...style
    }
  }, inner);
}
Object.assign(__ds_scope, { LINES, resolveLine, LineBullet });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/transit/LineBullet.jsx", error: String((e && e.message) || e) }); }

// components/core/Tag.jsx
try { (() => {
function Tag({
  children,
  line,
  variant = 'outline',
  style
}) {
  const c = line ? __ds_scope.resolveLine(line) : null;
  const solid = variant === 'solid' || !!c;
  const bg = c ? c.bg : solid ? 'var(--ink)' : 'transparent';
  const fg = c ? c.fg : solid ? 'var(--paper)' : 'var(--ink)';
  return /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 6,
      height: 24,
      padding: '0 8px',
      boxSizing: 'border-box',
      background: bg,
      color: fg,
      border: 'var(--border-w) solid ' + (c ? c.bg : 'var(--ink)'),
      borderRadius: 'var(--radius-0)',
      fontFamily: 'var(--font-sans)',
      fontSize: 11,
      fontWeight: 700,
      letterSpacing: 'var(--tracking-caps)',
      textTransform: 'uppercase',
      lineHeight: 1,
      whiteSpace: 'nowrap',
      ...style
    }
  }, children);
}
Object.assign(__ds_scope, { Tag });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/core/Tag.jsx", error: String((e && e.message) || e) }); }

// components/forms/Switch.jsx
try { (() => {
const {
  useState
} = React;
function Switch({
  label,
  checked,
  defaultChecked = false,
  onChange,
  line = 'green',
  disabled = false,
  style
}) {
  const [inner, setInner] = useState(defaultChecked);
  const on = checked !== undefined ? checked : inner;
  const c = __ds_scope.resolveLine(line);
  const toggle = () => {
    if (disabled) return;
    const n = !on;
    if (checked === undefined) setInner(n);
    onChange && onChange(n);
  };
  return /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: 10,
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? 0.45 : 1,
      fontFamily: 'var(--font-sans)',
      fontSize: 15,
      color: 'var(--ink)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("span", {
    role: "switch",
    "aria-checked": on,
    tabIndex: 0,
    onClick: toggle,
    onKeyDown: e => {
      if (e.key === ' ') {
        e.preventDefault();
        toggle();
      }
    },
    style: {
      position: 'relative',
      width: 48,
      height: 24,
      flexShrink: 0
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      left: 4,
      right: 4,
      top: 8,
      height: 8,
      background: on ? c.bg : 'var(--paper-3)',
      transition: 'background var(--dur-base) var(--ease-transit)'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      top: 0,
      left: on ? 24 : 0,
      width: 24,
      height: 24,
      borderRadius: '50%',
      boxSizing: 'border-box',
      background: on ? 'var(--ink)' : 'var(--white)',
      border: '4px solid var(--ink)',
      transition: 'left var(--dur-base) var(--ease-transit), background var(--dur-base) var(--ease-transit)'
    }
  })), label && /*#__PURE__*/React.createElement("span", {
    onClick: toggle
  }, label));
}
Object.assign(__ds_scope, { Switch });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Switch.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Tabs.jsx
try { (() => {
const {
  useState
} = React;
function Tabs({
  tabs = [],
  value,
  defaultValue,
  onChange,
  style
}) {
  const [inner, setInner] = useState(defaultValue ?? (tabs[0] && tabs[0].id));
  const cur = value !== undefined ? value : inner;
  const [hov, setHov] = useState(null);
  return /*#__PURE__*/React.createElement("div", {
    role: "tablist",
    style: {
      display: 'flex',
      gap: 4,
      boxShadow: 'inset 0 calc(-1 * var(--border-w)) 0 var(--ink)',
      fontFamily: 'var(--font-sans)',
      overflowX: 'auto',
      overflowY: 'hidden',
      ...style
    }
  }, tabs.map(t => {
    const a = t.id === cur;
    const c = __ds_scope.resolveLine(t.line || 'ink');
    return /*#__PURE__*/React.createElement("button", {
      key: t.id,
      role: "tab",
      "aria-selected": a,
      onClick: () => {
        if (value === undefined) setInner(t.id);
        onChange && onChange(t.id);
      },
      onMouseEnter: () => setHov(t.id),
      onMouseLeave: () => setHov(null),
      style: {
        position: 'relative',
        background: 'transparent',
        border: 0,
        padding: '12px 16px 14px',
        fontFamily: 'inherit',
        fontSize: 15,
        fontWeight: 700,
        color: a || hov === t.id ? 'var(--ink)' : 'var(--ink-3)',
        cursor: 'pointer',
        whiteSpace: 'nowrap'
      }
    }, t.label, /*#__PURE__*/React.createElement("span", {
      style: {
        position: 'absolute',
        left: 0,
        right: 0,
        bottom: 0,
        height: a ? 6 : 0,
        background: c.bg,
        transition: 'height var(--dur-fast) var(--ease-transit)'
      }
    }));
  }));
}
Object.assign(__ds_scope, { Tabs });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Tabs.jsx", error: String((e && e.message) || e) }); }

// components/transit/LineBundle.jsx
try { (() => {
function _sub(a, b) {
  return [a[0] - b[0], a[1] - b[1]];
}
function _add(a, b) {
  return [a[0] + b[0], a[1] + b[1]];
}
function _mul(a, k) {
  return [a[0] * k, a[1] * k];
}
function _unit(v) {
  const l = Math.hypot(v[0], v[1]) || 1;
  return [v[0] / l, v[1] / l];
}
function _dot(a, b) {
  return a[0] * b[0] + a[1] * b[1];
}
function _f(n) {
  return Math.round(n * 100) / 100;
}
function _clean(pts) {
  const out = [pts[0]];
  for (let i = 1; i < pts.length; i++) {
    const p = pts[i],
      q = out[out.length - 1];
    if (Math.hypot(p[0] - q[0], p[1] - q[1]) < 1e-6) continue;
    if (out.length >= 2) {
      const d1 = _unit(_sub(q, out[out.length - 2])),
        d2 = _unit(_sub(p, q));
      if (Math.abs(d1[0] * d2[1] - d1[1] * d2[0]) < 1e-6 && _dot(d1, d2) > 0) {
        out[out.length - 1] = p;
        continue;
      }
    }
    out.push(p);
  }
  return out;
}
function _angle(d1, d2) {
  return Math.acos(Math.max(-1, Math.min(1, _dot(d1, d2))));
}
function _radii(c, radius) {
  const rs = [];
  for (let i = 1; i < c.length - 1; i++) {
    const d1 = _unit(_sub(c[i], c[i - 1])),
      d2 = _unit(_sub(c[i + 1], c[i]));
    const tn = Math.tan(_angle(d1, d2) / 2);
    const lp = Math.hypot(..._sub(c[i], c[i - 1])) * (i === 1 ? 1 : 0.5),
      ln = Math.hypot(..._sub(c[i + 1], c[i])) * (i === c.length - 2 ? 1 : 0.5);
    const R = Array.isArray(radius) ? radius[i - 1] : radius;
    rs.push(tn > 1e-6 ? Math.min(R, Math.min(lp, ln) / tn) : R);
  }
  return rs;
}
function _offsetPts(c, o) {
  const n = c.length,
    dirs = [];
  for (let i = 0; i < n - 1; i++) dirs.push(_unit(_sub(c[i + 1], c[i])));
  const nr = dirs.map(d => [-d[1], d[0]]);
  return c.map((p, i) => {
    if (i === 0) return _add(p, _mul(nr[0], o));
    if (i === n - 1) return _add(p, _mul(nr[n - 2], o));
    const m = _add(nr[i - 1], nr[i]),
      k = 1 + _dot(nr[i - 1], nr[i]);
    return _add(p, _mul(m, o / k));
  });
}
function _toPath(p, rs) {
  let d = 'M' + _f(p[0][0]) + ' ' + _f(p[0][1]);
  for (let i = 1; i < p.length - 1; i++) {
    const d1 = _unit(_sub(p[i], p[i - 1])),
      d2 = _unit(_sub(p[i + 1], p[i])),
      th = _angle(d1, d2),
      r = rs[i - 1];
    if (th < 1e-4 || r <= 0) {
      d += ' L' + _f(p[i][0]) + ' ' + _f(p[i][1]);
      continue;
    }
    const t = r * Math.tan(th / 2),
      A = _sub(p[i], _mul(d1, t)),
      B = _add(p[i], _mul(d2, t)),
      cr = d1[0] * d2[1] - d1[1] * d2[0];
    d += ' L' + _f(A[0]) + ' ' + _f(A[1]) + ' A' + _f(r) + ' ' + _f(r) + ' 0 0 ' + (cr > 0 ? 1 : 0) + ' ' + _f(B[0]) + ' ' + _f(B[1]);
  }
  const e = p[p.length - 1];
  return d + ' L' + _f(e[0]) + ' ' + _f(e[1]);
}
/* waypoints -> tangent arcs -> per-line offsets. Offsets are along the left normal (-dy,dx); for a downward leg +o = towards -x.
   Arcs of every offset line share the centerline's arc centre, so bundles stay concentric (r - o*side). */
function _bundle(points, offsets, radius) {
  const c = _clean(points);
  if (c.length < 2) return offsets.map(() => '');
  const rs = _radii(c, radius),
    dirs = [];
  for (let i = 0; i < c.length - 1; i++) dirs.push(_unit(_sub(c[i + 1], c[i])));
  const nr = dirs.map(d => [-d[1], d[0]]);
  return offsets.map(o => {
    const p = _offsetPts(c, o);
    const r2 = rs.map((r, i) => {
      const s = _dot(nr[i], dirs[i + 1]) > 0 ? 1 : -1;
      return Math.max(0.01, r - o * s);
    });
    return _toPath(p, r2);
  });
}
const TransitGeometry = {
  bundle: (pts, offsets = [0], radius = 40) => _bundle(pts, offsets, radius),
  path: (pts, radius = 40) => _bundle(pts, [0], radius)[0],
  offsetPoints: _offsetPts,
  clean: _clean
};
function LineBundle({
  points = [],
  lines = ['vermilion', 'orange', 'yellow'],
  width = 10,
  gap = 4,
  radius,
  casing = true,
  casingColor = 'var(--paper)',
  viewBox,
  svgWidth,
  svgHeight,
  as = 'svg',
  style
}) {
  const n = lines.length,
    s = width + gap,
    bw = n * width + (n - 1) * gap,
    r = radius ?? bw * 1.6;
  const offs = lines.map((_, j) => ((n - 1) / 2 - j) * s);
  const ds = TransitGeometry.bundle(points, offs, r),
    cd = TransitGeometry.path(points, r);
  const g = /*#__PURE__*/React.createElement("g", {
    fill: "none",
    strokeLinecap: "round",
    strokeLinejoin: "round"
  }, casing && /*#__PURE__*/React.createElement("path", {
    d: cd,
    strokeWidth: bw + 2 * gap,
    style: {
      stroke: casingColor
    }
  }), ds.map((d, j) => /*#__PURE__*/React.createElement("path", {
    key: j,
    d: d,
    strokeWidth: width,
    style: {
      stroke: __ds_scope.resolveLine(lines[j]).bg
    }
  })));
  if (as === 'g') return g;
  let vb = viewBox;
  if (!vb && points.length) {
    const pad = bw / 2 + gap;
    const xs = points.map(p => p[0]),
      ys = points.map(p => p[1]);
    const x0 = Math.min(...xs) - pad,
      y0 = Math.min(...ys) - pad;
    vb = [x0, y0, Math.max(...xs) + pad - x0, Math.max(...ys) + pad - y0].join(' ');
  }
  return /*#__PURE__*/React.createElement("svg", {
    viewBox: vb,
    width: svgWidth,
    height: svgHeight,
    style: {
      display: 'block',
      overflow: 'visible',
      ...style
    },
    "aria-hidden": "true"
  }, g);
}
Object.assign(__ds_scope, { TransitGeometry, LineBundle });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/transit/LineBundle.jsx", error: String((e && e.message) || e) }); }

// components/brand/Logo.jsx
try { (() => {
const LogoGeometry = {
  mark: {
    box: 48,
    w: 6,
    gap: 3,
    r: 22.5,
    stem: [[16, 3], [16, 40], [45, 40]],
    offsets: [4.5, -4.5],
    bar: [[5, 12], [31, 12]]
  },
  favicon: {
    box: 16,
    w: 2.5,
    gap: 1.5,
    r: 6.5,
    stem: [[6, 1.5], [6, 12.5], [14.75, 12.5]],
    offsets: [2, -2],
    bar: [[1.5, 4.5], [11.5, 4.5]]
  }
};
function Logo({
  variant = 'lockup',
  tone = 'color',
  size = 40,
  wordmark = 'Transit Index',
  credit = false,
  style
}) {
  const uid = 'tim' + React.useId().replace(/[^a-zA-Z0-9]/g, '');
  const g = size <= 20 ? LogoGeometry.favicon : LogoGeometry.mark;
  const stems = __ds_scope.TransitGeometry.bundle(g.stem, g.offsets, g.r),
    bar = __ds_scope.TransitGeometry.path(g.bar, 1);
  const c = tone === 'mono' ? ['currentColor', 'currentColor', 'currentColor'] : ['var(--line-black)', 'var(--line-yellow)', 'var(--line-vermilion)'];
  const isMark = variant === 'mark';
  const mark = /*#__PURE__*/React.createElement("svg", {
    width: size,
    height: size,
    viewBox: '0 0 ' + g.box + ' ' + g.box,
    "aria-hidden": "true",
    style: {
      display: 'block',
      flexShrink: 0,
      overflow: 'visible'
    }
  }, /*#__PURE__*/React.createElement("defs", null, /*#__PURE__*/React.createElement("mask", {
    id: uid,
    maskUnits: "userSpaceOnUse",
    x: "-2",
    y: "-2",
    width: g.box + 4,
    height: g.box + 4
  }, /*#__PURE__*/React.createElement("rect", {
    x: "-2",
    y: "-2",
    width: g.box + 4,
    height: g.box + 4,
    fill: "#fff"
  }), /*#__PURE__*/React.createElement("path", {
    d: bar,
    fill: "none",
    stroke: "#000",
    strokeWidth: g.w + 2 * g.gap,
    strokeLinecap: "round"
  }))), /*#__PURE__*/React.createElement("g", {
    mask: 'url(#' + uid + ')',
    fill: "none",
    strokeWidth: g.w,
    strokeLinecap: "round",
    strokeLinejoin: "round"
  }, stems.map((d, i) => /*#__PURE__*/React.createElement("path", {
    key: i,
    d: d,
    style: {
      stroke: c[i]
    }
  }))), /*#__PURE__*/React.createElement("path", {
    d: bar,
    fill: "none",
    strokeWidth: g.w,
    strokeLinecap: "round",
    style: {
      stroke: c[2]
    }
  }));
  if (isMark) return /*#__PURE__*/React.createElement("span", {
    role: "img",
    "aria-label": wordmark,
    style: {
      display: 'inline-flex',
      color: 'var(--ink)',
      ...style
    }
  }, mark);
  return /*#__PURE__*/React.createElement("span", {
    role: "img",
    "aria-label": wordmark + (credit ? ' by GISBoost' : ''),
    style: {
      display: 'inline-flex',
      alignItems: 'center',
      gap: Math.round(size * 0.26),
      color: 'var(--ink)',
      fontFamily: 'var(--font-sans)',
      ...style
    }
  }, mark, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      lineHeight: 1
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      fontWeight: 700,
      fontSize: Math.round(size * 0.58),
      letterSpacing: '-0.035em',
      whiteSpace: 'nowrap'
    }
  }, wordmark), credit && /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: Math.max(10, Math.round(size * 0.24)),
      marginTop: Math.round(size * 0.1),
      color: 'var(--ink-3)',
      whiteSpace: 'nowrap'
    }
  }, "by GISBoost")));
}
Object.assign(__ds_scope, { LogoGeometry, Logo });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/Logo.jsx", error: String((e && e.message) || e) }); }

// components/transit/LineSwatch.jsx
try { (() => {
function LineSwatch({
  line = 'red',
  label,
  marker = false,
  height = 14,
  labelWidth = 88,
  style
}) {
  const c = __ds_scope.resolveLine(line);
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      fontFamily: 'var(--font-sans)',
      ...style
    }
  }, label != null && /*#__PURE__*/React.createElement("span", {
    style: {
      width: labelWidth,
      flexShrink: 0,
      fontSize: 13,
      fontWeight: 700,
      color: 'var(--ink)',
      whiteSpace: 'nowrap',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    }
  }, label), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      display: 'flex',
      gap: 6,
      height
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      background: c.bg,
      position: 'relative'
    }
  }, marker && /*#__PURE__*/React.createElement("span", {
    style: {
      position: 'absolute',
      right: 8,
      top: 0,
      bottom: 0,
      width: Math.max(4, Math.round(height * 0.55)),
      background: 'var(--ink)'
    }
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      width: Math.round(height * 1.3),
      background: c.bg
    }
  })));
}
Object.assign(__ds_scope, { LineSwatch });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/transit/LineSwatch.jsx", error: String((e && e.message) || e) }); }

// components/transit/RouteStrip.jsx
try { (() => {
function RouteStrip({
  stops = [],
  line = 'vermilion',
  current = -1,
  labelAngle = -40,
  thickness = 10,
  onStopClick,
  style
}) {
  const c = __ds_scope.resolveLine(line);
  const n = Math.max(1, stops.length);
  const rot = labelAngle !== 0;
  const LH = rot ? 120 : 0;
  const DOT = 28;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      display: 'grid',
      gridTemplateColumns: 'repeat(' + n + ',minmax(0,1fr))',
      fontFamily: 'var(--font-condensed)',
      color: 'var(--ink)',
      ...style
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      left: 'calc(100% / ' + 2 * n + ')',
      right: 'calc(100% / ' + 2 * n + ')',
      top: LH + DOT / 2 - thickness / 2,
      height: thickness,
      background: c.bg
    }
  }), stops.map((s, i) => {
    const x = !!(s.lines && s.lines.length);
    const cur = i === current;
    const big = x || s.terminus;
    const d = big ? 24 : 16;
    return /*#__PURE__*/React.createElement("div", {
      key: i,
      onClick: onStopClick ? () => onStopClick(i, s) : undefined,
      style: {
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        cursor: onStopClick ? 'pointer' : undefined,
        minWidth: 0
      }
    }, rot && /*#__PURE__*/React.createElement("div", {
      style: {
        height: LH,
        width: '100%',
        position: 'relative'
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        position: 'absolute',
        left: '50%',
        bottom: 4,
        transformOrigin: '0 100%',
        transform: 'rotate(' + labelAngle + 'deg)',
        whiteSpace: 'nowrap',
        fontSize: 13,
        fontWeight: cur || s.terminus ? 700 : 400,
        paddingLeft: 6
      }
    }, s.name)), /*#__PURE__*/React.createElement("div", {
      style: {
        height: DOT,
        display: 'flex',
        alignItems: 'center'
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        width: d,
        height: d,
        borderRadius: '50%',
        background: cur ? 'var(--ink)' : 'var(--white)',
        border: (big ? 4 : 3) + 'px solid ' + (big || cur ? 'var(--ink)' : c.bg),
        boxSizing: 'border-box',
        position: 'relative',
        zIndex: 1
      }
    })), !rot && /*#__PURE__*/React.createElement("span", {
      style: {
        marginTop: 6,
        fontSize: 12,
        fontWeight: cur || s.terminus ? 700 : 400,
        textAlign: 'center',
        textWrap: 'balance',
        lineHeight: 1.2,
        padding: '0 2px'
      }
    }, s.name), x && /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        gap: 3,
        marginTop: 6,
        flexWrap: 'wrap',
        justifyContent: 'center'
      }
    }, s.lines.map((l, j) => /*#__PURE__*/React.createElement(__ds_scope.LineBullet, {
      key: j,
      label: l.label,
      line: l.line,
      size: "xs"
    }))));
  }));
}
Object.assign(__ds_scope, { RouteStrip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/transit/RouteStrip.jsx", error: String((e && e.message) || e) }); }

// components/transit/SignArrow.jsx
try { (() => {
const DIR = {
  n: 'north',
  ne: 'north_east',
  e: 'east',
  se: 'south_east',
  s: 'south',
  sw: 'south_west',
  w: 'west',
  nw: 'north_west'
};
function SignArrow({
  direction = 'ne',
  line = 'yellow',
  size = 96,
  arrowColor,
  style
}) {
  const c = __ds_scope.resolveLine(line);
  return /*#__PURE__*/React.createElement("span", {
    role: "img",
    "aria-label": 'Arrow ' + direction,
    style: {
      width: size,
      height: size,
      borderRadius: '50%',
      background: c.bg,
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      flexShrink: 0,
      ...style
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: DIR[direction] || direction,
    size: Math.round(size * 0.7),
    color: arrowColor || c.fg
  }));
}
Object.assign(__ds_scope, { SignArrow });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/transit/SignArrow.jsx", error: String((e && e.message) || e) }); }

// components/transit/StationSign.jsx
try { (() => {
function StationSign({
  title,
  subtitle,
  lines = [],
  metaLeft,
  metaRight,
  exit,
  exitLines = [],
  exitDirection = 'north_west',
  size = 'md',
  style
}) {
  const lg = size === 'lg';
  const bs = lg ? 64 : 44;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--ink)',
      color: 'var(--paper)',
      borderRadius: 'var(--radius-sign)',
      overflow: 'hidden',
      fontFamily: 'var(--font-sans)',
      ...style
    }
  }, (metaLeft || metaRight) && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      gap: 16,
      padding: '10px 16px',
      fontSize: 13,
      borderBottom: '2px solid var(--paper)'
    }
  }, /*#__PURE__*/React.createElement("span", null, metaLeft), /*#__PURE__*/React.createElement("span", null, metaRight)), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: lg ? '20px 20px 24px' : '14px 16px 18px'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: lg ? 44 : 30,
      fontWeight: 400,
      letterSpacing: '-0.02em',
      lineHeight: 1.05,
      textWrap: 'balance'
    }
  }, title), subtitle && /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: lg ? 20 : 16,
      marginTop: 6,
      lineHeight: 1.25
    }
  }, subtitle), lines.length > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: lg ? 8 : 6,
      marginTop: lg ? 20 : 14
    }
  }, lines.map((l, i) => /*#__PURE__*/React.createElement(__ds_scope.LineBullet, {
    key: i,
    label: l.label,
    line: l.line,
    size: bs
  })))), exit && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'stretch',
      borderTop: '2px solid var(--paper)',
      background: 'var(--paper)',
      color: 'var(--ink)'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      alignItems: 'center',
      padding: '0 10px'
    }
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: exitDirection,
    size: 24
  })), /*#__PURE__*/React.createElement("span", {
    style: {
      background: 'var(--poster-red)',
      color: '#fff',
      fontWeight: 700,
      fontSize: 22,
      padding: '6px 12px',
      letterSpacing: '-0.02em'
    }
  }, "Exit"), /*#__PURE__*/React.createElement("span", {
    style: {
      flex: 1,
      display: 'flex',
      alignItems: 'center',
      padding: '4px 10px',
      fontSize: 14,
      lineHeight: 1.15
    }
  }, exit), exitLines.length > 0 && /*#__PURE__*/React.createElement("span", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 3,
      paddingRight: 10
    }
  }, exitLines.map((l, i) => /*#__PURE__*/React.createElement(__ds_scope.LineBullet, {
    key: i,
    label: l.label,
    line: l.line,
    size: "sm"
  })))));
}
Object.assign(__ds_scope, { StationSign });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/transit/StationSign.jsx", error: String((e && e.message) || e) }); }

// ui_kits/landing/Sections.jsx
try { (() => {
const TI = window.TransitIndexDesignSystem_923c60;
const fmt = (v, lang, d = 1) => Number(v).toLocaleString(lang === 'en' ? 'en-GB' : 'pl-PL', {
  minimumFractionDigits: d,
  maximumFractionDigits: d
});
function Kicker({
  children,
  bullet,
  line = 'vermilion',
  lane = 'R',
  terminus
}) {
  const {
    LineBullet
  } = TI;
  return /*#__PURE__*/React.createElement("div", {
    className: "kicker",
    "data-station": "",
    "data-lane": lane,
    "data-terminus": terminus ? '' : undefined
  }, bullet && /*#__PURE__*/React.createElement(LineBullet, {
    label: bullet,
    line: line,
    size: "sm"
  }), /*#__PURE__*/React.createElement("span", null, children));
}
function Header({
  t,
  lang,
  setLang,
  night,
  setNight
}) {
  const {
    Logo,
    IconButton,
    Button
  } = TI;
  return /*#__PURE__*/React.createElement("header", {
    className: "hdr"
  }, /*#__PURE__*/React.createElement("div", {
    className: "hdr-in"
  }, /*#__PURE__*/React.createElement("a", {
    href: "#top",
    style: {
      textDecoration: 'none'
    }
  }, /*#__PURE__*/React.createElement(Logo, {
    size: 30
  })), /*#__PURE__*/React.createElement("nav", {
    className: "hdr-nav"
  }, t.nav.map(([h, l]) => /*#__PURE__*/React.createElement("a", {
    key: h,
    href: h
  }, l))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 4,
      alignItems: 'center'
    }
  }, ['pl', 'en'].map(l => /*#__PURE__*/React.createElement(Button, {
    key: l,
    size: "sm",
    variant: lang === l ? 'primary' : 'ghost',
    onClick: () => setLang(l),
    style: {
      padding: '0 10px'
    }
  }, l.toUpperCase())), /*#__PURE__*/React.createElement(IconButton, {
    icon: night ? 'light_mode' : 'dark_mode',
    label: night ? t.day : t.night,
    onClick: () => setNight(!night)
  }))));
}
function Hero({
  t,
  lang
}) {
  const {
    Stat,
    Button
  } = TI;
  const h = t.hero;
  return /*#__PURE__*/React.createElement("section", {
    id: "top",
    className: "sec hero"
  }, /*#__PURE__*/React.createElement("div", {
    className: "col",
    "data-content-edge": ""
  }, /*#__PURE__*/React.createElement("div", {
    className: "kicker"
  }, h.kicker), /*#__PURE__*/React.createElement("h1", {
    className: "h1"
  }, h.title), /*#__PURE__*/React.createElement("p", {
    className: "lead"
  }, h.lead), /*#__PURE__*/React.createElement("div", {
    "data-station": "",
    "data-lane": "R",
    style: {
      position: 'relative',
      marginTop: 40,
      paddingRight: 120
    }
  }, /*#__PURE__*/React.createElement(Stat, {
    size: "xl",
    value: h.value,
    unit: "km/h",
    label: h.label,
    misregister: true
  }), /*#__PURE__*/React.createElement("div", {
    className: "stamp",
    "aria-hidden": "true"
  }, /*#__PURE__*/React.createElement("span", null, h.stamp[0]), /*#__PURE__*/React.createElement("b", null, h.stamp[1]), /*#__PURE__*/React.createElement("span", null, h.stamp[2]))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10,
      flexWrap: 'wrap',
      marginTop: 36
    }
  }, /*#__PURE__*/React.createElement("a", {
    href: "#ranking"
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "accent",
    iconRight: "south"
  }, h.cta1)), /*#__PURE__*/React.createElement("a", {
    href: "#mapa"
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    iconRight: "map"
  }, h.cta2)))));
}
function StretchStrip({
  n,
  lang
}) {
  const cls = v => v < 10 ? 1 : v < 14 ? 2 : v < 18 ? 3 : v < 22 ? 4 : 5;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      overflowX: 'auto',
      margin: '36px 0 0'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 560,
      display: 'grid',
      gridTemplateColumns: 'repeat(' + n.speeds.length + ',1fr)',
      position: 'relative',
      paddingBottom: 30
    }
  }, n.speeds.map((v, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      position: 'relative',
      paddingTop: 26
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--font-condensed)',
      fontWeight: 700,
      fontSize: 15,
      fontVariantNumeric: 'tabular-nums',
      position: 'absolute',
      top: 0,
      left: '50%',
      transform: 'translateX(-50%)',
      whiteSpace: 'nowrap'
    }
  }, fmt(v, lang), " km/h"), /*#__PURE__*/React.createElement("div", {
    style: {
      height: 10,
      background: 'var(--speed-' + cls(v) + ')'
    }
  }), /*#__PURE__*/React.createElement("span", {
    className: "stop",
    style: {
      left: -8
    }
  }), i === n.speeds.length - 1 && /*#__PURE__*/React.createElement("span", {
    className: "stop",
    style: {
      right: -8
    }
  }), /*#__PURE__*/React.createElement("div", {
    className: "stopname",
    style: {
      left: 0
    }
  }, n.stops[i]), i === n.speeds.length - 1 && /*#__PURE__*/React.createElement("div", {
    className: "stopname",
    style: {
      right: 0,
      transform: 'translateX(50%)'
    }
  }, n.stops[i + 1])))));
}
function NumberSec({
  t,
  lang
}) {
  const {
    Stat
  } = TI;
  const n = t.num;
  return /*#__PURE__*/React.createElement("section", {
    className: "sec"
  }, /*#__PURE__*/React.createElement("div", {
    className: "col"
  }, /*#__PURE__*/React.createElement(Kicker, {
    bullet: "02",
    line: "orange",
    lane: "L"
  }, n.kicker), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 28
    }
  }, /*#__PURE__*/React.createElement(Stat, {
    size: "lg",
    value: n.value
  })), /*#__PURE__*/React.createElement("h2", {
    className: "h2"
  }, n.title), /*#__PURE__*/React.createElement("p", {
    className: "lead"
  }, n.body), /*#__PURE__*/React.createElement(StretchStrip, {
    n: n,
    lang: lang
  }), /*#__PURE__*/React.createElement("div", {
    className: "kpis"
  }, n.kpis.map(([v, l]) => /*#__PURE__*/React.createElement(Stat, {
    key: l,
    size: "md",
    value: v,
    label: l
  })))));
}
function Ranking({
  t,
  lang
}) {
  const {
    RankingBar,
    Button
  } = TI;
  const r = t.rank;
  const ref = React.useRef(null);
  React.useEffect(() => {
    const bars = ref.current.querySelectorAll('[data-bar]');
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !window.gsap) return;
    const tw = gsap.fromTo(bars, {
      scaleX: 0
    }, {
      scaleX: 1,
      duration: .9,
      ease: 'power3.out',
      stagger: .05,
      scrollTrigger: {
        trigger: ref.current,
        start: 'top 72%',
        once: true
      }
    });
    return () => tw.scrollTrigger && tw.scrollTrigger.kill();
  }, []);
  return /*#__PURE__*/React.createElement("section", {
    id: "ranking",
    className: "sec"
  }, /*#__PURE__*/React.createElement("div", {
    className: "col"
  }, /*#__PURE__*/React.createElement(Kicker, {
    bullet: "03",
    line: "yellow",
    lane: "R"
  }, r.kicker), /*#__PURE__*/React.createElement("h2", {
    className: "h2"
  }, r.title), /*#__PURE__*/React.createElement("p", {
    className: "small"
  }, r.note), /*#__PURE__*/React.createElement("div", {
    ref: ref,
    style: {
      marginTop: 24,
      borderTop: '2px solid var(--ink)'
    }
  }, window.TI_CITIES.map((c, i) => /*#__PURE__*/React.createElement(RankingBar, {
    key: c.pl,
    rank: i + 1,
    label: c[lang],
    value: c.v,
    max: 22,
    locale: lang,
    flag: c.flag,
    flagLabel: c.flag ? r[c.flag] : undefined,
    highlight: c.hl
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 20
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "ghost",
    iconRight: "download"
  }, r.more))));
}
const ROUTES = [{
  pts: [[20, 300], [180, 300], [260, 220], [260, 30]],
  cls: [4, 3, 't3', 2, 1]
}, {
  pts: [[40, 80], [200, 80], [300, 180], [580, 180]],
  cls: [5, 4, 4, 3, 'n', 3]
}, {
  pts: [[120, 370], [120, 270], [220, 170], [420, 170], [510, 80], [590, 80]],
  cls: [2, 1, 'n', 2, 3, 4, 5]
}, {
  pts: [[340, 370], [340, 270], [440, 270], [530, 360]],
  cls: [3, 't2', 2, 1]
}];
function MapTeaser() {
  const ref = React.useRef(null);
  const [geo, setGeo] = React.useState(null);
  const TG = TI.TransitGeometry;
  const ds = React.useMemo(() => ROUTES.map(r => TG.path(r.pts, 30)), []);
  React.useLayoutEffect(() => {
    const ps = [...ref.current.querySelectorAll('[data-route]')];
    setGeo(ps.map((p, i) => {
      const L = p.getTotalLength(),
        n = ROUTES[i].cls.length,
        cuts = [...Array(n + 1)].map((_, k) => L * k / n);
      return {
        L,
        cuts,
        stops: cuts.map(c => {
          const q = p.getPointAtLength(c);
          return [q.x, q.y];
        })
      };
    }));
  }, []);
  const dash = (g, k, thin) => {
    const a = g.cuts[k],
      b = g.cuts[k + 1];
    const arr = [0, a];
    if (thin) {
      let x = 0;
      while (x < b - a) {
        const d = Math.min(6, b - a - x);
        arr.push(d, 4);
        x += 10;
      }
      arr[arr.length - 1] = g.L * 2;
    } else arr.push(b - a, g.L * 2);
    return arr.join(' ');
  };
  return /*#__PURE__*/React.createElement("svg", {
    ref: ref,
    viewBox: "0 0 600 380",
    style: {
      display: 'block',
      width: '100%',
      height: 'auto',
      background: 'var(--map-base)'
    },
    role: "img",
    "aria-label": "Schematic speed map preview"
  }, [60, 140, 220, 300].map(y => /*#__PURE__*/React.createElement("line", {
    key: 'h' + y,
    x1: "0",
    x2: "600",
    y1: y + 20,
    y2: y + 20,
    strokeWidth: "6",
    style: {
      stroke: 'var(--map-street)'
    }
  })), [90, 300, 470].map(x => /*#__PURE__*/React.createElement("line", {
    key: 'v' + x,
    y1: "0",
    y2: "380",
    x1: x,
    x2: x,
    strokeWidth: "6",
    style: {
      stroke: 'var(--map-street)'
    }
  })), ROUTES.map((r, i) => /*#__PURE__*/React.createElement("g", {
    key: i,
    fill: "none",
    strokeLinecap: "butt"
  }, /*#__PURE__*/React.createElement("path", {
    "data-route": "",
    d: ds[i],
    strokeWidth: "12",
    strokeLinecap: "round",
    style: {
      stroke: 'var(--map-base)'
    }
  }), geo && r.cls.map((c, k) => {
    const nd = c === 'n',
      thin = typeof c === 'string' && c[0] === 't';
    const col = nd ? 'var(--speed-nodata)' : 'var(--speed-' + (thin ? c.slice(1) : c) + ')';
    return /*#__PURE__*/React.createElement("path", {
      key: k,
      d: ds[i],
      strokeWidth: "6",
      strokeDasharray: dash(geo[i], k, thin),
      style: {
        stroke: col
      }
    });
  }), geo && geo[i].stops.map(([x, y], k) => /*#__PURE__*/React.createElement("circle", {
    key: k,
    cx: x,
    cy: y,
    r: "3.4",
    strokeWidth: "1.6",
    style: {
      fill: 'var(--map-base)',
      stroke: 'var(--ink)'
    }
  })))));
}
function MapSec({
  t
}) {
  const {
    SpeedLegend,
    Button
  } = TI;
  const m = t.map,
    l = m.legend;
  return /*#__PURE__*/React.createElement("section", {
    id: "mapa",
    className: "sec"
  }, /*#__PURE__*/React.createElement("div", {
    className: "col"
  }, /*#__PURE__*/React.createElement(Kicker, {
    bullet: "04",
    line: "sky",
    lane: "L"
  }, m.kicker), /*#__PURE__*/React.createElement("h2", {
    className: "h2"
  }, m.title), /*#__PURE__*/React.createElement("p", {
    className: "lead"
  }, m.body), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 28,
      border: '2px solid var(--ink)'
    }
  }, /*#__PURE__*/React.createElement(MapTeaser, null), /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--map-base)',
      borderTop: '2px solid var(--ink)',
      padding: 16
    }
  }, /*#__PURE__*/React.createElement(SpeedLegend, {
    title: l.title,
    slowLabel: l.slow,
    fastLabel: l.fast,
    noDataLabel: l.nd,
    thinLabel: l.thin
  }))), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 20
    }
  }, /*#__PURE__*/React.createElement(Button, {
    iconRight: "open_in_full"
  }, m.cta))));
}
function Limits({
  t
}) {
  const {
    LineBullet,
    Button
  } = TI;
  const x = t.lim;
  return /*#__PURE__*/React.createElement("section", {
    id: "ograniczenia",
    className: "sec"
  }, /*#__PURE__*/React.createElement("div", {
    className: "col"
  }, /*#__PURE__*/React.createElement(Kicker, {
    bullet: "05",
    line: "blue",
    lane: "R"
  }, x.kicker), /*#__PURE__*/React.createElement("h2", {
    className: "h2"
  }, x.title), /*#__PURE__*/React.createElement("div", {
    className: "limits"
  }, x.items.map(([h, d], i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      borderTop: '2px solid var(--ink)',
      paddingTop: 14,
      display: 'flex',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement(LineBullet, {
    label: i + 1,
    line: "black",
    size: "sm"
  }), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("b", {
    style: {
      fontSize: 18,
      letterSpacing: '-0.01em'
    }
  }, h), /*#__PURE__*/React.createElement("p", {
    className: "small",
    style: {
      margin: '6px 0 0'
    }
  }, d))))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 10,
      flexWrap: 'wrap',
      marginTop: 28
    }
  }, x.links.map(([l, ic]) => /*#__PURE__*/React.createElement(Button, {
    key: l,
    variant: "secondary",
    iconLeft: ic
  }, l)))));
}
function Footer({
  t
}) {
  const {
    Logo
  } = TI;
  const f = t.foot;
  const Col = ({
    h,
    items
  }) => /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    className: "kicker",
    style: {
      marginBottom: 10
    }
  }, h), items.map(i => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      fontSize: 15,
      lineHeight: 1.9
    }
  }, /*#__PURE__*/React.createElement("a", {
    href: "#top",
    style: {
      textDecorationThickness: 1
    }
  }, i))));
  return /*#__PURE__*/React.createElement("footer", {
    className: "sec foot"
  }, /*#__PURE__*/React.createElement("div", {
    className: "col"
  }, /*#__PURE__*/React.createElement(Kicker, {
    lane: "L",
    terminus: true
  }, f.kicker), /*#__PURE__*/React.createElement("div", {
    className: "foot-cols"
  }, /*#__PURE__*/React.createElement(Col, {
    h: f.ed,
    items: f.eds
  }), /*#__PURE__*/React.createElement(Col, {
    h: f.dl,
    items: f.dls
  }), /*#__PURE__*/React.createElement(Col, {
    h: f.about,
    items: f.abouts
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-end',
      gap: 16,
      flexWrap: 'wrap',
      marginTop: 56,
      paddingTop: 20,
      borderTop: '2px solid var(--ink)'
    }
  }, /*#__PURE__*/React.createElement(Logo, {
    size: 28,
    credit: true
  }), /*#__PURE__*/React.createElement("span", {
    className: "small",
    style: {
      color: 'var(--ink-3)'
    }
  }, f.note))));
}
Object.assign(window, {
  Header,
  Hero,
  NumberSec,
  Ranking,
  MapSec,
  Limits,
  Footer
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/landing/Sections.jsx", error: String((e && e.message) || e) }); }

// ui_kits/landing/copy.js
try { (() => {
window.TI_CITIES = [{
  pl: 'Praga',
  en: 'Prague',
  v: 20.8
}, {
  pl: 'Wiedeń',
  en: 'Vienna',
  v: 20.1
}, {
  pl: 'Wrocław',
  en: 'Wrocław',
  v: 19.2
}, {
  pl: 'Poznań',
  en: 'Poznań',
  v: 18.7
}, {
  pl: 'Gdańsk',
  en: 'Gdańsk',
  v: 18.4
}, {
  pl: 'Budapeszt',
  en: 'Budapest',
  v: 17.9
}, {
  pl: 'Kraków',
  en: 'Kraków',
  v: 17.2
}, {
  pl: 'Warszawa',
  en: 'Warsaw',
  v: 17.0,
  hl: true
}, {
  pl: 'Berlin',
  en: 'Berlin',
  v: 16.6
}, {
  pl: 'Łódź',
  en: 'Łódź',
  v: 16.1,
  flag: 'gaps'
}, {
  pl: 'Wilno',
  en: 'Vilnius',
  v: 15.8,
  flag: 'thin'
}, {
  pl: 'Bratysława',
  en: 'Bratislava',
  v: 15.2
}];
window.TI_COPY = {
  pl: {
    nav: [['#ranking', 'Ranking'], ['#mapa', 'Mapa'], ['#ograniczenia', 'Metodologia']],
    night: 'Wydanie nocne',
    day: 'Wydanie dzienne',
    hero: {
      kicker: 'Wydanie 01 · wrzesień 2026',
      title: 'Jak naprawdę jeździ komunikacja miejska',
      lead: 'Prędkość autobusów i tramwajów w 12 miastach, policzona z pozycji pojazdów — nie z rozkładu.',
      value: '17,6',
      label: 'mediana zmierzonej prędkości autobusów i tramwajów, 12 miast',
      cta1: 'Zobacz ranking',
      cta2: 'Otwórz mapę',
      stamp: ['Wydanie', '01', '09 · 2026']
    },
    num: {
      kicker: '02 · Liczba',
      value: '−22%',
      title: 'Tyle wolniej jadą pojazdy niż najszybsze przejazdy tych samych odcinków.',
      body: 'Odcinek to fragment trasy między dwoma kolejnymi przystankami. Dla każdego porównujemy medianę zmierzonej prędkości z 10% najszybszych przejazdów.',
      stops: ['Rondo ONZ', 'Rondo Daszyńskiego', 'Płocka', 'Młynarska', 'Wola Ratusz', 'Os. Górczewska'],
      speeds: [11.2, 8.9, 14.6, 19.3, 12.8],
      kpis: [['12', 'miast'], ['3,8 mln', 'pozycji pojazdów dziennie'], ['41 200', 'odcinków']]
    },
    rank: {
      kicker: '03 · Ranking',
      title: 'Miasta według zmierzonej prędkości',
      note: 'Mediana dla autobusów i tramwajów, dni robocze 6:00–20:00. Flagi oznaczają ograniczenia danych.',
      thin: 'mała próba',
      gaps: 'luki w danych',
      more: 'Pełny ranking i pobieranie'
    },
    map: {
      kicker: '04 · Mapa',
      title: 'Każdy odcinek w kolorze swojej prędkości',
      body: 'Pełnoekranowa mapa pokazuje wszystkie odcinki między przystankami. Poniżej podgląd schematyczny, nie rzeczywista sieć.',
      cta: 'Otwórz mapę Warszawy',
      legend: {
        title: 'Prędkość',
        slow: 'wolniej',
        fast: 'szybciej',
        nd: 'brak danych',
        thin: 'mała próba'
      }
    },
    lim: {
      kicker: '05 · Uczciwie',
      title: 'Czego te dane nie mówią',
      items: [['To rekonstrukcja.', 'Pojazdy raportują pozycję co 10–30 s. Przejazd między odczytami odtwarzamy — nie mierzymy go wprost.'], ['Nie każdy odcinek ma próbę.', 'Odcinki z mniej niż 30 przejazdami oznaczamy kreskowaniem i nie wliczamy do rankingu.'], ['Strumienie mają luki.', 'Gdy operator nie publikuje danych GTFS-Realtime, odcinek jest szary, a miasto dostaje flagę.'], ['Rozkład nie jest wzorcem.', 'Spowolnienie liczymy względem szybkich przejazdów. Rozkład pokazujemy obok, dla porównania.']],
      links: [['Metodologia', 'menu_book'], ['Jakość danych', 'fact_check']]
    },
    foot: {
      kicker: 'Stacja końcowa',
      ed: 'Wydania',
      eds: ['Wydanie 01 · wrzesień 2026 — bieżące'],
      dl: 'Pobierz',
      dls: ['Ranking (CSV)', 'Odcinki (GeoPackage)', 'Profile godzinowe (CSV)'],
      about: 'O projekcie',
      abouts: ['Metodologia', 'Jakość danych', 'Kontakt'],
      note: 'Wszystkie liczby na tej stronie są poglądowe.'
    }
  },
  en: {
    nav: [['#ranking', 'Ranking'], ['#mapa', 'Map'], ['#ograniczenia', 'Methodology']],
    night: 'Night edition',
    day: 'Day edition',
    hero: {
      kicker: 'Edition 01 · September 2026',
      title: 'How public transport really moves',
      lead: 'Bus and tram speeds in 12 cities, computed from vehicle positions — not from timetables.',
      value: '17.6',
      label: 'median measured speed of buses and trams, 12 cities',
      cta1: 'See the ranking',
      cta2: 'Open the map',
      stamp: ['Edition', '01', '09 · 2026']
    },
    num: {
      kicker: '02 · The number',
      value: '−22%',
      title: 'That is how much slower vehicles run than the fastest trips on the same stretches.',
      body: 'A stretch is the part of a route between two consecutive stops. For each one we compare the median measured speed with the fastest 10% of trips.',
      stops: ['Rondo ONZ', 'Rondo Daszyńskiego', 'Płocka', 'Młynarska', 'Wola Ratusz', 'Os. Górczewska'],
      speeds: [11.2, 8.9, 14.6, 19.3, 12.8],
      kpis: [['12', 'cities'], ['3.8 M', 'vehicle positions a day'], ['41,200', 'stretches']]
    },
    rank: {
      kicker: '03 · Ranking',
      title: 'Cities by measured speed',
      note: 'Median for buses and trams, weekdays 6:00–20:00. Flags mark data limitations.',
      thin: 'thin sample',
      gaps: 'feed gaps',
      more: 'Full ranking and downloads'
    },
    map: {
      kicker: '04 · Map',
      title: 'Every stretch coloured by its speed',
      body: 'The full-screen map shows every stretch between stops. Below is a schematic preview, not the real network.',
      cta: 'Open the Warsaw map',
      legend: {
        title: 'Speed',
        slow: 'slower',
        fast: 'faster',
        nd: 'no data',
        thin: 'thin sample'
      }
    },
    lim: {
      kicker: '05 · Honestly',
      title: 'What these data don’t tell you',
      items: [['It is a reconstruction.', 'Vehicles report their position every 10–30 s. We rebuild the trip between pings — we don’t measure it directly.'], ['Not every stretch has a sample.', 'Stretches with fewer than 30 trips are hatched and left out of the ranking.'], ['Feeds have gaps.', 'When an operator doesn’t publish GTFS-Realtime, the stretch is grey and the city is flagged.'], ['The timetable is not the benchmark.', 'Slowdown is measured against fast trips. The timetable is shown alongside for comparison.']],
      links: [['Methodology', 'menu_book'], ['Data quality', 'fact_check']]
    },
    foot: {
      kicker: 'Terminus',
      ed: 'Editions',
      eds: ['Edition 01 · September 2026 — current'],
      dl: 'Download',
      dls: ['Ranking (CSV)', 'Stretches (GeoPackage)', 'Hourly profiles (CSV)'],
      about: 'About',
      abouts: ['Methodology', 'Data quality', 'Contact'],
      note: 'All figures on this page are illustrative.'
    }
  }
};
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/landing/copy.js", error: String((e && e.message) || e) }); }

// ui_kits/landing/journey.js
try { (() => {
(function () {
  var NSN = 'TransitIndexDesignSystem_923c60',
    SVGNS = 'http://www.w3.org/2000/svg';
  var KEYS_A = ['vermilion', 'orange', 'yellow'],
    KEYS_B = ['sky', 'blue'],
    DEL = [0, 0.035, 0.07, 0.02, 0.055];
  var triggers = [],
    tweens = [],
    entryDone = false,
    timer = null,
    lastW = window.innerWidth;
  function reduced() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches || !window.gsap || !window.ScrollTrigger;
  }
  function mk(tag, attrs, parent) {
    var e = document.createElementNS(SVGNS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }
  function build() {
    var NS = window[NSN],
      svg = document.getElementById('journey');
    if (!NS || !NS.TransitGeometry || !svg) return;
    var TG = NS.TransitGeometry;
    triggers.forEach(function (t) {
      t.kill();
    });
    tweens.forEach(function (t) {
      t.kill();
    });
    triggers = [];
    tweens = [];
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    svg.style.height = '0px';
    var W = document.documentElement.clientWidth,
      H = document.documentElement.scrollHeight;
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.style.width = W + 'px';
    svg.style.height = H + 'px';
    var edge = document.querySelector('[data-content-edge]'),
      cr = edge ? edge.getBoundingClientRect().right : W * 0.6;
    var w = 10,
      g = 4,
      bw = 5 * w + 4 * g,
      cs = cr + 56 + bw / 2,
      ce = W - 40 - bw / 2,
      mobile = ce - cs < 200;
    if (mobile) {
      w = 4;
      g = 2;
      bw = 5 * w + 4 * g;
    }
    var s = w + g,
      r = bw * 1.6,
      lanes = mobile ? {
        L: 14 + bw / 2,
        R: 14 + bw / 2
      } : {
        L: cs,
        R: ce
      };
    var st = [].slice.call(document.querySelectorAll('[data-station]')).map(function (e) {
      var b = e.getBoundingClientRect();
      return {
        y: Math.round(b.top + window.scrollY + b.height / 2),
        x: lanes[e.getAttribute('data-lane') || 'R'],
        term: e.hasAttribute('data-terminus')
      };
    });
    if (st.length < 2) return;
    var root = mk('g', {}, svg),
      nodes = mk('g', {}, svg);
    function bundle(parent, main, lineOffs, casingOff, keys) {
      var gEl = mk('g', {
        fill: 'none',
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round'
      }, parent);
      var cas = mk('path', {
        d: TG.bundle(main, [casingOff], r)[0],
        'stroke-width': keys.length * w + (keys.length - 1) * g + 2 * g
      }, gEl);
      cas.style.stroke = 'var(--paper)';
      var lines = TG.bundle(main, lineOffs, r).map(function (d, j) {
        var p = mk('path', {
          d: d,
          'stroke-width': w
        }, gEl);
        p.style.stroke = 'var(--line-' + keys[j] + ')';
        return p;
      });
      return {
        cas: cas,
        lines: lines
      };
    }
    var s0 = st[0],
      ey = Math.max(96, s0.y - r * 2.4);
    var entryMain = mobile ? [[s0.x, -20], [s0.x, s0.y]] : [[W + bw, ey], [s0.x, ey], [s0.x, s0.y]];
    var eA = bundle(root, entryMain, [2 * s, s, 0], s, KEYS_A),
      eB = bundle(root, entryMain, [-s, -2 * s], -1.5 * s, KEYS_B);
    var segs = [],
      cA = -s,
      cB = 1.5 * s;
    for (var k = 0; k < st.length - 1; k++) {
      var a = st[k],
        b = st[k + 1],
        h = b.y - a.y,
        dx = b.x - a.x,
        adx = Math.abs(dx),
        mA,
        mB;
      if (adx < 1) {
        mA = [[a.x + cA, a.y], [a.x + cA, b.y]];
        mB = [[a.x + cB, a.y], [a.x + cB, b.y]];
      } else {
        var yL = a.y + Math.max(r, h * 0.2),
          yF = yL + Math.max(bw * 2.2, h * 0.18);
        if (yF + adx + r > b.y) {
          yF = b.y - adx - r;
          yL = Math.min(yL, yF - bw * 2.2);
          if (yL < a.y + r * 0.6) {
            yL = yF = a.y + Math.max(r * 0.6, (h - adx) / 2);
          }
        }
        var leadA = dx > 0,
          ya = leadA ? yL : yF,
          yb = leadA ? yF : yL;
        mA = [[a.x + cA, a.y], [a.x + cA, ya], [b.x + cA, ya + adx], [b.x + cA, b.y]];
        mB = [[a.x + cB, a.y], [a.x + cB, yb], [b.x + cB, yb + adx], [b.x + cB, b.y]];
      }
      var grp = mk('g', {}, root),
        pA,
        pB;
      if (k % 2 === 0) {
        pB = bundle(grp, mB, [s / 2, -s / 2], 0, KEYS_B);
        pA = bundle(grp, mA, [s, 0, -s], 0, KEYS_A);
      } else {
        pA = bundle(grp, mA, [s, 0, -s], 0, KEYS_A);
        pB = bundle(grp, mB, [s / 2, -s / 2], 0, KEYS_B);
      }
      segs.push({
        a: a,
        b: b,
        A: pA,
        B: pB
      });
    }
    st.forEach(function (p) {
      var hh = w + 14,
        rc = mk('rect', {
          x: p.x - bw / 2 - 9,
          y: p.y - hh / 2,
          width: bw + 18,
          height: hh,
          rx: hh / 2,
          'stroke-width': mobile ? 2 : 3
        }, nodes);
      rc.style.fill = p.term ? 'var(--ink)' : 'var(--paper)';
      rc.style.stroke = 'var(--ink)';
    });
    var head = mk('g', {
        opacity: 0
      }, nodes),
      hc = mk('circle', {
        r: w * 1.15
      }, head),
      hi = mk('circle', {
        r: w * 0.45
      }, head);
    hc.style.fill = 'var(--ink)';
    hi.style.fill = 'var(--paper)';
    if (reduced()) return;
    var gs = window.gsap,
      vh = window.innerHeight;
    function prep(p) {
      var L = p.getTotalLength();
      p.style.strokeDasharray = L + ' ' + L;
      p.style.strokeDashoffset = L;
      p._L = L;
      return p;
    }
    if (!entryDone && window.scrollY < 10) {
      var tl0 = gs.timeline({
        delay: .25,
        onComplete: function () {
          entryDone = true;
        }
      });
      [eA, eB].forEach(function (part, bi) {
        prep(part.cas);
        tl0.to(part.cas, {
          strokeDashoffset: 0,
          duration: 1.6,
          ease: 'power2.inOut'
        }, bi * 0.12);
        part.lines.forEach(function (p, j) {
          prep(p);
          tl0.to(p, {
            strokeDashoffset: 0,
            duration: 1.6,
            ease: 'power2.inOut'
          }, (bi * 3 + j) * 0.06);
        });
      });
      tweens.push(tl0);
    } else entryDone = true;
    segs.forEach(function (sg) {
      var tl = gs.timeline({
        paused: true
      });
      [sg.A, sg.B].forEach(function (part, bi) {
        var dl = part.lines.map(function (_, j) {
            return DEL[bi * 3 + j];
          }),
          mn = Math.min.apply(null, dl);
        prep(part.cas);
        tl.to(part.cas, {
          strokeDashoffset: 0,
          duration: 1 - mn,
          ease: 'none'
        }, mn);
        part.lines.forEach(function (p, j) {
          prep(p);
          tl.to(p, {
            strokeDashoffset: 0,
            duration: 1 - dl[j],
            ease: 'none'
          }, dl[j]);
        });
      });
      var lead = sg.A.lines[1];
      tl.eventCallback('onUpdate', function () {
        var p = (tl.progress() - DEL[1]) / (1 - DEL[1]);
        if (p > 0.002 && p < 0.998) {
          var pt = lead.getPointAtLength(lead._L * p);
          head.setAttribute('transform', 'translate(' + pt.x.toFixed(1) + ' ' + pt.y.toFixed(1) + ')');
          head.setAttribute('opacity', '1');
        } else head.setAttribute('opacity', '0');
      });
      var start = Math.max(0, sg.a.y - vh * 0.6),
        end = Math.max(start + 1, sg.b.y - vh * 0.6);
      triggers.push(ScrollTrigger.create({
        start: start,
        end: end,
        animation: tl,
        scrub: 0.6
      }));
      tweens.push(tl);
    });
  }
  function schedule() {
    clearTimeout(timer);
    timer = setTimeout(function () {
      build();
      if (window.ScrollTrigger) ScrollTrigger.refresh();
    }, 160);
  }
  window.addEventListener('resize', function () {
    if (window.innerWidth !== lastW) {
      lastW = window.innerWidth;
      schedule();
    }
  });
  window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', schedule);
  window.TIJourney = {
    build: build,
    schedule: schedule
  };
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/landing/journey.js", error: String((e && e.message) || e) }); }

__ds_ns.LogoGeometry = __ds_scope.LogoGeometry;

__ds_ns.Logo = __ds_scope.Logo;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.Card = __ds_scope.Card;

__ds_ns.Icon = __ds_scope.Icon;

__ds_ns.IconButton = __ds_scope.IconButton;

__ds_ns.Tag = __ds_scope.Tag;

__ds_ns.RankingBar = __ds_scope.RankingBar;

__ds_ns.SpeedLegend = __ds_scope.SpeedLegend;

__ds_ns.Stat = __ds_scope.Stat;

__ds_ns.Dialog = __ds_scope.Dialog;

__ds_ns.Toast = __ds_scope.Toast;

__ds_ns.Tooltip = __ds_scope.Tooltip;

__ds_ns.Checkbox = __ds_scope.Checkbox;

__ds_ns.Input = __ds_scope.Input;

__ds_ns.Radio = __ds_scope.Radio;

__ds_ns.Select = __ds_scope.Select;

__ds_ns.Switch = __ds_scope.Switch;

__ds_ns.Tabs = __ds_scope.Tabs;

__ds_ns.LINES = __ds_scope.LINES;

__ds_ns.LineBullet = __ds_scope.LineBullet;

__ds_ns.TransitGeometry = __ds_scope.TransitGeometry;

__ds_ns.LineBundle = __ds_scope.LineBundle;

__ds_ns.LineSwatch = __ds_scope.LineSwatch;

__ds_ns.RouteStrip = __ds_scope.RouteStrip;

__ds_ns.SignArrow = __ds_scope.SignArrow;

__ds_ns.StationSign = __ds_scope.StationSign;

})();
