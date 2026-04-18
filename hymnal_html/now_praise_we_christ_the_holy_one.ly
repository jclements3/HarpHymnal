\version "2.22.1"

\header {
  title = "173  Now Praise We Christ, the Holy One"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key e \minor
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne d'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf f'4 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'4 g'4 \acciaccatura { g'16 ees'16 } f'4 | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "2" } } } g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } c''4 c''4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } b'4 c''2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iiiii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'4 c''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } b'4 a'4 aes'4 | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'4 c''4 a'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'8 f'4 e'2 | \acciaccatura { fis'16 d'16 } e'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } | }
    { \voiceTwo <e g b>1\p\arpeggio | <fis a c'>1\arpeggio | <e fis a c'>1\arpeggio | <b d' fis'>1\arpeggio | <a c' e'>1\arpeggio | <d' b'>1\arpeggio | fis'1 | <fis a c'>1\arpeggio | <c' e' g'>1\arpeggio | <a d' fis'>1\arpeggio | <a, d fis>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <b, d fis>1\p\arpeggio | \acciaccatura { g,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 e,4 | \acciaccatura { a,,8 } <fis, a, b, d>4\arpeggio a,8 b,8 d8 a,8 e4 | \acciaccatura { d,8 } <a, c e>4\arpeggio c8 e8 c8 e8 d4 | \acciaccatura { c,8 } <fis, a, c>4\arpeggio a,8 c8 a,8 c8 b,4 | \acciaccatura { a,,8 } <fis, a, c>4\arpeggio a,8 c8 a,8 c8 b,4 | \acciaccatura { a,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 a,4 | \acciaccatura { g,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 b,4 | \acciaccatura { a,,8 } <fis, a, c>4\arpeggio a,8 c8 a,8 c8 fis,4 | \acciaccatura { e,8 } <c e g>4\arpeggio e8 g8 e8 g8 fis4 | \acciaccatura { e,8 } <c e g>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
