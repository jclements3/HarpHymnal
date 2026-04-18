\version "2.22.1"

\header {
  title = "135  Jesus, In Thy Dying Woes"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key d \minor
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf f'4 g'4 f'4 | e'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } d'8 \acciaccatura { e'16 c'16 } d'2 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } f'4 e'4 d'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } f'4 e'2 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" "7" } } } a'4 c''4 a'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'4 a'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 a'4 f'4 | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { e'16 c'16 } d'2 | }
    { \voiceTwo <g c' e'>1\p\arpeggio | <g c'>1\arpeggio | bes1 | <a c'>1\arpeggio | <f g bes d'>1\arpeggio | <d' f'>1\arpeggio | d'1 | <g c'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <bes, d f>1\p\arpeggio | \acciaccatura { d,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { d,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 bes,4 | \acciaccatura { a,,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 bes,4 | \acciaccatura { a,,8 } <f, a, c e>4\arpeggio a,8 c8 e8 a,8 g,4 | \acciaccatura { f,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 g,4 | \acciaccatura { f,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 e4 | \acciaccatura { d,8 } <bes, d f>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
