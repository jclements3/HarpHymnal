\version "2.22.1"

\header {
  title = "192  O Lord, How Shall I Meet Thee"
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
    { \voiceOne ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf g'4 aes'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4 aes'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } aes'4 g'4 ees'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'4 \acciaccatura { f'16 d'16 } ees'2 | ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 aes'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4 aes'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } aes'4 g'4 ees'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'4 \acciaccatura { f'16 d'16 } ees'2 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''4 d''4 | ees''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''4 \acciaccatura { d''16 bes'16 } c''2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 c''4 bes'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 f'2 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } ees'4 \acciaccatura { g'16 ees'16 } f'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } bes'4 aes'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } bes'4 aes'4 g'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } f'4 \acciaccatura { f'16 d'16 } ees'2 | }
    { \voiceTwo <ees g bes>1\p\arpeggio | <c' ees' g'>1\arpeggio | c'1 | <f aes c'>1\arpeggio | <ees g bes>1\arpeggio | <c' ees' g'>1\arpeggio | c'1 | <f aes c'>1\arpeggio | <ees' g'>1\arpeggio | <ees' g' bes'>1\arpeggio | <c' ees'>1\arpeggio | <ees g bes>1\arpeggio | <d f aes bes>1\arpeggio | <d' f'>1\arpeggio | <d' f'>1\arpeggio | <d f aes bes>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { ees,8 } <bes, d f>1\p\arpeggio | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d4 | \acciaccatura { c,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 g,4 | \acciaccatura { f,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 ees,4 | \acciaccatura { ees,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d4 | \acciaccatura { c,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 g,4 | \acciaccatura { f,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 ees,4 | \acciaccatura { ees,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 f,4 | \acciaccatura { ees,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d4 | \acciaccatura { c,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 f4 | \acciaccatura { ees,8 } <ees, g, bes, c>4\arpeggio g,8 bes,8 c8 g,8 ees,4 | \acciaccatura { ees,8 } <ees, g, bes, c>4\arpeggio g,8 bes,8 c8 g,8 f,4 | \acciaccatura { ees,8 } <ees, g, bes, c>4\arpeggio g,8 bes,8 c8 g,8 f,4 | \acciaccatura { ees,8 } <ees, g, bes, c>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
