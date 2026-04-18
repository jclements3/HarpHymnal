\version "2.22.1"

\header {
  title = "062  Day of Wrath, O Day of Mourning"
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
    { \voiceOne f'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf e'8 d'4 e'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 a'4 d'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'4 a'4 \acciaccatura { e'16 c'16 } d'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } f'4 e'4 fis'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 g'4 \acciaccatura { g'16 e'16 } f'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } f'4 e'4 d'4 | f'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'8 bes'4. a'8 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'4 bes'4 f'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 bes'4. a'8 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 bes'4 f'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } d''4 d''4. d'8 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 f'2 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } e'4 \acciaccatura { e'16 c'16 } d'2 | }
    { \voiceTwo <g c'>1\p\arpeggio | bes1 | <c' e' g'>1\arpeggio | c'1 | <f a c'>1\arpeggio | bes1 | d'1 | <g bes d'>1\arpeggio | <g bes d'>1\arpeggio | d'1 | <g c' e'>1\arpeggio | <d f a>1\arpeggio | <g bes>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <bes, d f>1\p\arpeggio | \acciaccatura { d,8 } <e, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 a,4 | \acciaccatura { g,,8 } <e, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 e,4 | \acciaccatura { e,8 } <e, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 a,4 | \acciaccatura { g,,8 } <e, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 e,4 | \acciaccatura { a,,8 } <a, c e>4\arpeggio c8 e8 c8 e8 e,4 | \acciaccatura { d,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { f,8 } <d, f, a,>4\arpeggio f,8 a,8 f,8 a,8 c4 | \acciaccatura { bes,,8 } <d, f, a,>4\arpeggio f,8 a,8 f,8 a,8 g,4 | \acciaccatura { f,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 e4 | \acciaccatura { d,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 e4 | \acciaccatura { d,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 g,4 | \acciaccatura { f,8 } <d, f, a,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
