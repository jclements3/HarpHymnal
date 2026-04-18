\version "2.22.1"

\header {
  title = "125  Jesus Christ Is Risen Today"
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
    { \voiceOne c'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf e'4 g'4 c'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'4 a'4 g'4 | e'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } f'8 g'8 c'8 f'4 e'8 f'8 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'4 c'2 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 a'4 \acciaccatura { a'16 f'16 } g'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } e'4 e'4 d'4 | e'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } f'8 g'8 c'8 f'4 e'8 f'8 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d'4 \acciaccatura { d'16 b16 } c'2 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''4 d''4 g'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''4 \acciaccatura { f''16 d''16 } e''2 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''8 d''8 g'8 c''4 b'8 c''8 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4 g'2 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } a'8 b'8 g'8 c''4 \acciaccatura { f'16 d'16 } e'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'4 a'4 g'4 | c''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } b'8 c''8 g'8 a'8 b'8 c''8 d''8 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } b'4 \acciaccatura { d''16 b'16 } c''2 | }
    { \voiceTwo <f a>1\p\arpeggio | <f a c'>1\arpeggio | <b d'>1\arpeggio | <f a>1\arpeggio | <f a c'>1\arpeggio | <d f a>1\arpeggio | <b d'>1\arpeggio | <c e g>1\arpeggio | <c' e'>1\arpeggio | <c' e' g'>1\arpeggio | <e' a'>1\arpeggio | <e a c'>1\arpeggio | <g b d'>1\arpeggio | <f a c'>1\arpeggio | f'1 | <f' a'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { c,8 } <c, e, g,>1\p\arpeggio | \acciaccatura { f,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 d,4 | \acciaccatura { c,8 } <c, e, g, a,>4\arpeggio e,8 g,8 a,8 e,8 c,4 | \acciaccatura { c,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 g,4 | \acciaccatura { f,8 } <d, f, a,>4\arpeggio f,8 a,8 f,8 a,8 d,4 | \acciaccatura { d,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 d,4 | \acciaccatura { c,8 } <c, e, g, a,>4\arpeggio e,8 g,8 a,8 e,8 d,4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 g,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 d,4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 g,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 f,4 | \acciaccatura { f,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 d,4 | \acciaccatura { c,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 d,4 | \acciaccatura { c,8 } <c, e, g,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
