\version "2.22.1"

\header {
  title = "155  Lord, Dismiss Us With Thy Blessing"
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
    { \voiceOne g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } }\mf e'4 c''4 g'4 | e''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''8 c''4 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } a'4 g'4 \acciaccatura { d''16 b'16 } c''4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } f'4 e'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } e'4 c''4 g'4 | e''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''8 c''4 b'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } b'4 a'4 b'8 c''8 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4 g'2 | d''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } d''8 b'4 g'4 | e''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } d''8 c''4 \acciaccatura { b'16 g'16 } a'4 | f''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } e''4 d''4 c''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } b'4 \acciaccatura { d''16 b'16 } c''2 | }
    { \voiceTwo <b d' f'>1\p\arpeggio | <f' a'>1\arpeggio | <g b d'>1\arpeggio | c'1 | b'1 | <e' g'>1\arpeggio | <g b d'>1\arpeggio | <e a c'>1\arpeggio | f'1 | <b c' e' g'>1\arpeggio | <d' f' a'>1\arpeggio | <f' a'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { c,8 } <c, e, g, a,>1\p\arpeggio | \acciaccatura { c,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 g,4 | \acciaccatura { f,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 f,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 d,4 | \acciaccatura { c,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 d,4 | \acciaccatura { c,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 f,4 | \acciaccatura { e,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, c e>4\arpeggio b,8 c8 e8 b,8 d,4 | \acciaccatura { c,8 } <c, d, f, a,>4\arpeggio d,8 f,8 a,8 d,8 c,4 | \acciaccatura { d,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 d,4 | \acciaccatura { c,8 } <c, e, g,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
