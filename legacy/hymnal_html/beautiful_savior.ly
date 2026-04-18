\version "2.22.1"

\header {
  title = "037  Beautiful Savior"
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
    { \voiceOne ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf ees'4 ees'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'4 \acciaccatura { f'16 d'16 } ees'2 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 g'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'4 \acciaccatura { aes'16 f'16 } g'2 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } ees''4 c''4 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } aes'4 \acciaccatura { aes'16 f'16 } g'4 | aes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'2 | f'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''4 \acciaccatura { c''16 aes'16 } bes'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 aes'2 | aes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } bes'4 aes'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } f'4 \acciaccatura { aes'16 f'16 } g'2 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } g'4 g'4 | bes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } aes'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } f'2 | \acciaccatura { f'16 d'16 } ees'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <f aes c'>1\p\arpeggio | <f aes c'>1\arpeggio | <f aes c'>1\arpeggio | <f aes c'>1\arpeggio | <d' ees' g'>1\arpeggio | <d' ees'>1\arpeggio | <bes d' f'>1\arpeggio | <aes bes d'>1\arpeggio | <ees' g'>1\arpeggio | <c' ees'>1\arpeggio | <aes bes d' f'>1\arpeggio | <aes bes d'>1\arpeggio | <d f aes bes>1\arpeggio | <d' f'>1\arpeggio | <d f aes bes>1\arpeggio | <aes c'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { ees,8 } <ees, g, bes,>1\p\arpeggio | \acciaccatura { f,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 ees,4 | \acciaccatura { ees,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 g,4 | \acciaccatura { f,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 ees,4 | \acciaccatura { ees,8 } <ees, f, aes, c>4\arpeggio f,8 aes,8 c8 f,8 f,4 | \acciaccatura { ees,8 } <ees, f, aes, c>4\arpeggio f,8 aes,8 c8 f,8 ees,4 | \acciaccatura { f,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 c4 | \acciaccatura { bes,,8 } <bes, d ees g>4\arpeggio d8 ees8 g8 d8 f,4 | \acciaccatura { ees,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 c4 | \acciaccatura { c,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d ees g>4\arpeggio d8 ees8 g8 d8 c4 | \acciaccatura { bes,,8 } <bes, d ees g>4\arpeggio d8 ees8 g8 d8 bes,4 | \acciaccatura { ees,8 } <ees, g, bes, c>4\arpeggio g,8 bes,8 c8 g,8 f,4 | \acciaccatura { ees,8 } <ees, g, bes, c>4\arpeggio g,8 bes,8 c8 g,8 f,4 | \acciaccatura { ees,8 } <ees, g, bes, c>4\arpeggio g,8 bes,8 c8 g,8 f,4 | \acciaccatura { ees,8 } <ees, g, bes,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
