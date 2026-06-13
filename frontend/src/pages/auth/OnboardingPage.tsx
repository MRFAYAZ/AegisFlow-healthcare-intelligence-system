import { useState } from 'react'

interface Props { onDone: () => void }

const slides = [
  {
    icon: (
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
        <rect width="64" height="64" rx="16" fill="#eff6ff"/>
        <path d="M32 14 C32 14 18 21 18 32 C18 40.8 24.3 46 32 46 C39.7 46 46 40.8 46 32 C46 21 32 14 32 14Z" stroke="#2563eb" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
        <path d="M25 32 L29.5 36.5 L39 27" stroke="#2563eb" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
    title: 'Predict shortages before they happen',
    desc: 'AegisFlow monitors inventory levels across all registered facilities in real time and alerts you days before a critical shortage hits.',
    color: '#2563eb',
    bg: '#eff6ff',
  },
  {
    icon: (
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
        <rect width="64" height="64" rx="16" fill="#fef2f2"/>
        <circle cx="32" cy="32" r="14" stroke="#dc2626" strokeWidth="2.5" fill="none"/>
        <path d="M32 25 L32 33" stroke="#dc2626" strokeWidth="2.5" strokeLinecap="round"/>
        <circle cx="32" cy="38" r="1.5" fill="#dc2626"/>
      </svg>
    ),
    title: 'Instant emergency alerts',
    desc: 'When a facility hits zero stock on a critical medicine, emergency protocols activate automatically — nearest donors are located within seconds.',
    color: '#dc2626',
    bg: '#fef2f2',
  },
  {
    icon: (
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
        <rect width="64" height="64" rx="16" fill="#f0fdf4"/>
        <path d="M20 32 L44 32" stroke="#16a34a" strokeWidth="2.5" strokeLinecap="round"/>
        <path d="M36 24 L44 32 L36 40" stroke="#16a34a" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
        <path d="M20 20 L20 44" stroke="#16a34a" strokeWidth="2.5" strokeLinecap="round"/>
      </svg>
    ),
    title: 'Redistribute. Save lives.',
    desc: 'Coordinate medicine transfers between hospitals, clinics, and pharmacies. Track every shipment end-to-end with full audit trails.',
    color: '#16a34a',
    bg: '#f0fdf4',
  },
  {
    icon: (
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
        <rect width="64" height="64" rx="16" fill="#fffbeb"/>
        <circle cx="24" cy="36" r="5" stroke="#d97706" strokeWidth="2.2" fill="none"/>
        <circle cx="40" cy="36" r="5" stroke="#d97706" strokeWidth="2.2" fill="none"/>
        <circle cx="32" cy="22" r="5" stroke="#d97706" strokeWidth="2.2" fill="none"/>
        <line x1="28.5" y1="26.8" x2="25.5" y2="30.8" stroke="#d97706" strokeWidth="1.8"/>
        <line x1="35.5" y1="26.8" x2="38.5" y2="30.8" stroke="#d97706" strokeWidth="1.8"/>
        <line x1="29" y1="36" x2="35" y2="36" stroke="#d97706" strokeWidth="1.8"/>
      </svg>
    ),
    title: 'Intelligence for every role',
    desc: 'Tailored dashboards for system admins, hospital staff, pharmacists, and emergency operators. Everyone sees exactly what they need.',
    color: '#d97706',
    bg: '#fffbeb',
  },
]

export function OnboardingPage({ onDone }: Props) {
  const [current, setCurrent] = useState(0)
  const [animating, setAnimating] = useState(false)

  function goTo(index: number) {
    if (animating || index === current) return
    setAnimating(true)
    setTimeout(() => { setCurrent(index); setAnimating(false) }, 200)
  }

  function next() {
    if (current < slides.length - 1) goTo(current + 1)
    else onDone()
  }

  function skip() { onDone() }

  const slide = slides[current]

  return (
    <div style={{
      minHeight:'100vh', background:'#f5f4f0', display:'flex', alignItems:'center', justifyContent:'center', padding:24,
      fontFamily:'-apple-system,Inter,sans-serif'
    }}>
      <div style={{ width:'100%', maxWidth:440 }}>

        {/* Skip */}
        <div style={{ display:'flex', justifyContent:'flex-end', marginBottom:32 }}>
          <button onClick={skip} style={{ background:'none', border:'none', cursor:'pointer', fontSize:12, color:'#9a9890', padding:'4px 8px' }}>
            Skip
          </button>
        </div>

        {/* Card */}
        <div style={{
          background:'#ffffff', borderRadius:16, border:'1px solid #e5e3de',
          padding:'40px 36px', textAlign:'center',
          boxShadow:'0 2px 16px rgba(0,0,0,0.06)',
          opacity: animating ? 0 : 1,
          transform: animating ? 'translateY(8px)' : 'translateY(0)',
          transition:'all 0.2s ease'
        }}>
          {/* Icon */}
          <div style={{ display:'flex', justifyContent:'center', marginBottom:28 }}>
            {slide.icon}
          </div>

          {/* Step indicator */}
          <div style={{ fontSize:11, color:'#9a9890', marginBottom:14, letterSpacing:'0.3px' }}>
            {current + 1} of {slides.length}
          </div>

          {/* Title */}
          <div style={{ fontSize:20, fontWeight:600, color:'#1a1916', lineHeight:1.3, marginBottom:14, letterSpacing:'-0.3px' }}>
            {slide.title}
          </div>

          {/* Desc */}
          <div style={{ fontSize:13, color:'#6b6860', lineHeight:1.7, marginBottom:36 }}>
            {slide.desc}
          </div>

          {/* Dots */}
          <div style={{ display:'flex', justifyContent:'center', gap:6, marginBottom:32 }}>
            {slides.map((_, i) => (
              <button key={i} onClick={() => goTo(i)} style={{
                width: i === current ? 20 : 7, height:7,
                borderRadius:4, border:'none', cursor:'pointer',
                background: i === current ? slide.color : '#e5e3de',
                transition:'all 0.25s ease', padding:0,
              }}/>
            ))}
          </div>

          {/* CTA */}
          <button onClick={next} style={{
            width:'100%', padding:'12px 24px', borderRadius:9,
            background: slide.color, border:'none', cursor:'pointer',
            fontSize:13, fontWeight:600, color:'#ffffff',
            transition:'opacity 0.15s',
          }}
          onMouseEnter={e => (e.currentTarget.style.opacity='0.88')}
          onMouseLeave={e => (e.currentTarget.style.opacity='1')}
          >
            {current === slides.length - 1 ? 'Get started →' : 'Next →'}
          </button>
        </div>

        {/* Logo at bottom */}
        <div style={{ textAlign:'center', marginTop:24, display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
          <div style={{ width:22, height:22, background:'#1d4ed8', borderRadius:6, display:'flex', alignItems:'center', justifyContent:'center' }}>
            <span style={{ color:'#fff', fontSize:11, fontWeight:700 }}>A</span>
          </div>
          <span style={{ fontSize:13, fontWeight:600, color:'#1a1916' }}>AegisFlow</span>
        </div>
      </div>
    </div>
  )
}
