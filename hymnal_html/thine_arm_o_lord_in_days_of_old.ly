\version "2.22.1"

\header {
  title = "262  Thine Arm, O Lord, in Days of Old"
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
    { \voiceOne g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf fis'8 e'4 e'4 e'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } g'4 g'4 \acciaccatura { b'16 g'16 } a'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } a'8 b'4 b'4 a'8 g'8 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'2. | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } fis'8 e'4 e'4 e'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 g'4 a'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'8 b'4 b'4 a'8 g'8 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { fis'16 d'16 } e'2. | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''8 d''4 b'4 b'8 a'8 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'4 a'4 b'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'8 b'4 b'8 a'8 g'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'2. | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'8 e'4 e'4 e'8 d'8 | e'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'8 g'4 g'4 \acciaccatura { b'16 g'16 } a'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'8 b'4 b'4 a'8 g'8 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { fis'16 d'16 } e'2. | }
    { \voiceTwo <e g b>1\p\arpeggio | <d fis a b>1\arpeggio | <d' fis'>1\arpeggio | <fis a c'>1\arpeggio | <e g b>1\arpeggio | <e g b>1\arpeggio | e'1 | <e g b>1\arpeggio | <e' g'>1\arpeggio | <a c' e'>1\arpeggio | <a c' e'>1\arpeggio | <fis a c'>1\arpeggio | <fis a c'>1\arpeggio | <fis a c'>1\arpeggio | e'1 | <a, d fis>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { e,8 } <c e g>1\p\arpeggio | \acciaccatura { g,,8 } <e, g, b, c>4\arpeggio g,8 b,8 c8 g,8 e,4 | \acciaccatura { g,,8 } <e, g, b, c>4\arpeggio g,8 b,8 c8 g,8 a,4 | \acciaccatura { g,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 a,4 | \acciaccatura { g,,8 } <c e g>4\arpeggio e8 g8 e8 g8 a,4 | \acciaccatura { g,,8 } <c e g>4\arpeggio e8 g8 e8 g8 a,4 | \acciaccatura { g,,8 } <c e g>4\arpeggio e8 g8 e8 g8 fis4 | \acciaccatura { e,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { e,8 } <c e g>4\arpeggio e8 g8 e8 g8 a,4 | \acciaccatura { g,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 a,4 | \acciaccatura { g,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 a,4 | \acciaccatura { g,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 a,4 | \acciaccatura { g,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 b,4 | \acciaccatura { a,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 e,4 | \acciaccatura { g,,8 } <c e g>4\arpeggio e8 g8 e8 g8 fis4 | \acciaccatura { e,8 } <c e g>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
