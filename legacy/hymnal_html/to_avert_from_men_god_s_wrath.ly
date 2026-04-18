\version "2.22.1"

\header {
  title = "268  To Avert From Men God's Wrath"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key ees \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf ees'4 f'4 g'4 | aes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } aes'8 \acciaccatura { aes'16 f'16 } g'2 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } ees'4 f'4 g'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'4 \acciaccatura { f'16 d'16 } ees'2 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 bes'4 bes'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''4 \acciaccatura { c''16 aes'16 } bes'2 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 bes'4 bes'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''4 bes'2 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } ees'4 f'4 \acciaccatura { aes'16 f'16 } g'4 | aes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } aes'8 g'2 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } f'4 g'4 f'4 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } d'4 \acciaccatura { f'16 d'16 } ees'2 | }
    { \voiceTwo <aes c'>1\p\arpeggio | <aes c' ees'>1\arpeggio | <aes c'>1\arpeggio | <aes c'>1\arpeggio | <aes c'>1\arpeggio | <aes c' ees'>1\arpeggio | r1 | <ees' g'>1\arpeggio | <d ees g bes>1\arpeggio | <aes c' ees'>1\arpeggio | <ees g bes>1\arpeggio | <g c'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { ees,8 } <ees, g, bes,>1\p\arpeggio | \acciaccatura { aes,,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 ees,4 | \acciaccatura { ees,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 f,4 | \acciaccatura { ees,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 ees,4 | \acciaccatura { ees,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 bes,4 | \acciaccatura { aes,,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 ees,4 | \acciaccatura { ees,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 f,4 | \acciaccatura { ees,8 } <ees, g, aes, c>4\arpeggio g,8 aes,8 c8 g,8 ees,4 | \acciaccatura { aes,,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 f,4 | \acciaccatura { ees,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <aes, bes, d f>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
