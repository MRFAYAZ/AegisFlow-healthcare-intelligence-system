import { useEffect, useState } from 'react'

interface Props { onDone: () => void }

export function SplashScreen({ onDone }: Props) {
  const [phase, setPhase] = useState<'in'|'hold'|'out'>('in')

  useEffect(() => {
    const t1 = setTimeout(() => setPhase('hold'), 400)
    const t2 = setTimeout(() => setPhase('out'), 2200)
    const t3 = setTimeout(() => onDone(), 2800)
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3) }
  }, [onDone])

  return (
    <div
      style={{
        position:'fixed', inset:0, background:'#ffffff', zIndex:9999,
        display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center',
        transition:'opacity 0.55s ease',
        opacity: phase === 'out' ? 0 : 1,
      }}
    >
      {/* Logo mark */}
      <div style={{
        transform: phase === 'in' ? 'scale(0.7) translateY(12px)' : 'scale(1) translateY(0)',
        opacity: phase === 'in' ? 0 : 1,
        transition: 'all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
        display:'flex', flexDirection:'column', alignItems:'center', gap:20
      }}>
        {/* Icon */}
        <div style={{
          width:72, height:72, background:'#1d4ed8', borderRadius:20,
          display:'flex', alignItems:'center', justifyContent:'center',
          boxShadow:'0 8px 32px rgba(29,78,216,0.25)'
        }}>
          <svg width="38" height="38" viewBox="0 0 38 38" fill="none">
            <path d="M19 6 C19 6 8 12 8 21 C8 27.6 13 32 19 32 C25 32 30 27.6 30 21 C30 12 19 6 19 6Z" stroke="white" strokeWidth="2.2" fill="none" strokeLinecap="round"/>
            <path d="M13 21 L16.5 24.5 L25 16" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>

        {/* Name */}
        <div style={{ textAlign:'center' }}>
          <div style={{ fontSize:28, fontWeight:700, color:'#1a1916', letterSpacing:'-0.5px', fontFamily:'-apple-system,Inter,sans-serif' }}>
            AegisFlow
          </div>
          <div style={{ fontSize:13, color:'#9a9890', marginTop:4, fontFamily:'-apple-system,Inter,sans-serif', letterSpacing:'0.3px' }}>
            Healthcare Intelligence Platform
          </div>
        </div>

        {/* Tagline */}
        <div style={{ display:'flex', gap:8, alignItems:'center', marginTop:4 }}>
          {['Predict','Alert','Redistribute','Heal'].map((word, i) => (
            <div key={word} style={{ display:'flex', alignItems:'center', gap:8 }}>
              <span style={{
                fontSize:11, color:'#6b6860', fontFamily:'-apple-system,Inter,sans-serif',
                opacity: phase === 'hold' ? 1 : 0,
                transform: phase === 'hold' ? 'translateY(0)' : 'translateY(4px)',
                transition: `all 0.4s ease ${0.1 + i * 0.08}s`
              }}>{word}</span>
              {i < 3 && <span style={{ color:'#d0cec8', fontSize:10 }}>·</span>}
            </div>
          ))}
        </div>

        {/* Loader */}
        <div style={{ marginTop:24, width:160, height:2, background:'#f0eeea', borderRadius:2, overflow:'hidden' }}>
          <div style={{
            height:'100%', background:'#2563eb', borderRadius:2,
            width: phase === 'hold' ? '100%' : '0%',
            transition: 'width 1.4s ease 0.3s'
          }}/>
        </div>
      </div>

      {/* Bottom */}
      <div style={{
        position:'absolute', bottom:32, fontSize:11, color:'#d0cec8',
        fontFamily:'-apple-system,Inter,sans-serif', letterSpacing:'0.3px'
      }}>
        Bengaluru · Karnataka
      </div>
    </div>
  )
}
