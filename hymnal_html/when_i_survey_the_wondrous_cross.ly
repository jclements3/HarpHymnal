\version "2.22.1"

\header {
  title = "285  When I Survey the Wondrous Cross"
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
    { \voiceOne ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf g'4 aes'4 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } c''4 d''4 | ees''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''4 \acciaccatura { d''16 bes'16 } c''4 | bes'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } bes'4 \acciaccatura { c''16 aes'16 } bes'4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'2 | aes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } \acciaccatura { aes'16 f'16 } g'2 | f'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } g'4 \acciaccatura { g'16 ees'16 } f'4 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } g'4 bes'4 ees''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } bes'4 aes'4 g'4 | f'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } c''4 \acciaccatura { ees''16 c''16 } d''4 | ees''2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } aes'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } f'2 | \acciaccatura { f'16 d'16 } ees'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <aes c'>1\p\arpeggio | <d' f' aes'>1\arpeggio | <ees' g' bes'>1\arpeggio | <ees' g'>1\arpeggio | <d' ees' g'>1\arpeggio | <aes c' ees'>1\arpeggio | <bes d' f'>1\arpeggio | <aes bes d'>1\arpeggio | <d ees g bes>1\arpeggio | d'1 | <bes d' f'>1\arpeggio | <aes bes d'>1\arpeggio | <d' f' aes'>1\arpeggio | c''1 | <d f aes bes>1\arpeggio | <aes c'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { ees,8 } <ees, g, bes,>1\p\arpeggio | \acciaccatura { ees,8 } <ees, g, bes, c>4\arpeggio g,8 bes,8 c8 g,8 f,4 | \acciaccatura { ees,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 f,4 | \acciaccatura { ees,8 } <ees, g, aes, c>4\arpeggio g,8 aes,8 c8 g,8 ees,4 | \acciaccatura { aes,,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 g,4 | \acciaccatura { f,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 f,4 | \acciaccatura { bes,,8 } <bes, d ees g>4\arpeggio d8 ees8 g8 d8 f,4 | \acciaccatura { ees,8 } <ees, g, aes, c>4\arpeggio g,8 aes,8 c8 g,8 ees,4 | \acciaccatura { ees,8 } <ees, g, aes, c>4\arpeggio g,8 aes,8 c8 g,8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 c4 | \acciaccatura { bes,,8 } <bes, d ees g>4\arpeggio d8 ees8 g8 d8 f,4 | \acciaccatura { ees,8 } <ees, g, bes, c>4\arpeggio g,8 bes,8 c8 g,8 ees,4 | \acciaccatura { ees,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 f,4 | \acciaccatura { ees,8 } <ees, g, bes, c>4\arpeggio g,8 bes,8 c8 g,8 f,4 | \acciaccatura { ees,8 } <ees, g, bes,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
