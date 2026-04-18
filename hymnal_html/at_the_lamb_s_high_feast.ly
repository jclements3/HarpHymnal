\version "2.22.1"

\header {
  title = "028  At The Lamb's High Feast"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key c \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne c'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf g'4 c''4 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'16 g'16 a'8 a'8 \acciaccatura { a'16 f'16 } g'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } a'4 b'4 a'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'8 g'8 f'8 e'2 | e'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } d'8 e'8 f'8 g'8 g'8 c'4 | e'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'8 e'8 c'8 b8 c'8 d'8 f'8 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } d'4 \acciaccatura { d'16 b16 } c'2 | }
    { \voiceTwo <d' f' a'>1\p\arpeggio | <f a c'>1\arpeggio | <f a c'>1\arpeggio | <e g b>1\arpeggio | b1 | <f a>1\arpeggio | a1 | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { c,8 } <c, e, g,>1\p\arpeggio | \acciaccatura { d,8 } <d, f, a,>4\arpeggio f,8 a,8 f,8 a,8 d,4 | \acciaccatura { f,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 f,4 | \acciaccatura { e,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 d,4 | \acciaccatura { c,8 } <c, e, g, a,>4\arpeggio e,8 g,8 a,8 e,8 d,4 | \acciaccatura { c,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 g,4 | \acciaccatura { f,8 } <f, a, c>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
