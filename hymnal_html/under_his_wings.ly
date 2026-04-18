\version "2.22.1"

\header {
  title = "274  Under His Wings"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key des \major
  \time 6/4
}

upper = {
  \global
  <<
    { \voiceOne f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf ges'4 g'4 aes'2 aes'8 aes'8 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4 f'4 aes'4 ges'2 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } f'4 ges'4 bes'4 aes'4 aes'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } ees'4 e'4 \acciaccatura { ges'16 ees'16 } f'2. | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } ges'4 g'4 aes'4 aes'4 des''4 | ees''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } des''4 bes'4 bes'4 aes'2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''4 des''4 des''4 aes'4 \acciaccatura { ges'16 ees'16 } f'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } ges'4 ees'4 des'2. | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } f'4 aes'4 des''2. | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4 c''4 \acciaccatura { ees''16 c''16 } des''2. | des''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } aes'4 f'4 bes'4 aes'4 f'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { f'16 des'16 } ees'1 | des'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'4 aes'4 des''2 c''4 | ees''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } des''4 bes'4 \acciaccatura { bes'16 ges'16 } aes'2. | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''4 des''4 aes'4 f'4 des'4 | ees'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } \acciaccatura { ees'16 c'16 } des'2 | }
    { \voiceTwo des'1.\p | des'1. | <ges aes c'>1.\arpeggio | <c' des'>1.\arpeggio | <c' des'>1.\arpeggio | ges'1. | des'1. | f'1. | des'1. | <des' f' aes'>1.\arpeggio | des'1. | <des f aes>1.\arpeggio | <ees' ges' bes'>1.\arpeggio | <ees' ges'>1.\arpeggio | r1. | <aes, bes, des f>1.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { des,8 } <aes, c ees>1.\p\arpeggio | \acciaccatura { des,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 bes,4 | \acciaccatura { aes,,8 } <aes, c des f>4\arpeggio c8 des8 f8 c8 des8 f8 c8 des8 ees,4 | \acciaccatura { des,8 } <des, f, ges, bes,>4\arpeggio f,8 ges,8 bes,8 f,8 ges,8 bes,8 f,8 ges,8 des,4 | \acciaccatura { des,8 } <des, f, ges, bes,>4\arpeggio f,8 ges,8 bes,8 f,8 ges,8 bes,8 f,8 ges,8 aes,4 | \acciaccatura { ges,8 } <des, f, aes,>4\arpeggio f,8 aes,8 f,8 aes,8 f,8 aes,8 f,8 aes,8 ees,4 | \acciaccatura { des,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 aes,4 | \acciaccatura { aes,,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 ees,4 | \acciaccatura { des,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 aes,4 | \acciaccatura { des,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 aes,4 | \acciaccatura { des,8 } <des, f, aes,>4\arpeggio f,8 aes,8 f,8 aes,8 f,8 aes,8 f,8 aes,8 f,4 | \acciaccatura { ees,8 } <des, f, aes,>4\arpeggio f,8 aes,8 f,8 aes,8 f,8 aes,8 f,8 aes,8 des,4 | \acciaccatura { des,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees ges>1.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
