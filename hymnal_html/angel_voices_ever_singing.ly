\version "2.22.1"

\header {
  title = "024  Angel Voices, Ever Singing"
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
    { \voiceOne e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf g'4 a'4 g'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } a'4 g'4 e'4 | c'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d'4 e'4 f'4 | d'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } g'4 c''4 \acciaccatura { b'16 g'16 } a'4 | d''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } c''8 b'4 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } e'4 g'4 fis'4 | \acciaccatura { a'16 f'16 } g'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 g'4 a'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'4 f'4 g'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 a'4 \acciaccatura { d''16 b'16 } c''4 | d''2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } b'4 | \acciaccatura { d''16 b'16 } c''1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <f a c'>1\p\arpeggio | <a c'>1\arpeggio | a1 | <f g b>1\arpeggio | <b c'>1\arpeggio | <a c' e'>1\arpeggio | <a c'>1\arpeggio | <g b d'>1\arpeggio | <e g b>1\arpeggio | <d f a>1\arpeggio | c'1 | <f' g'>1\arpeggio | <f' a'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { c,8 } <c, e, g,>1\p\arpeggio | \acciaccatura { f,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 b,4 | \acciaccatura { a,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, c e>4\arpeggio b,8 c8 e8 b,8 d,4 | \acciaccatura { c,8 } <c, d, f, a,>4\arpeggio d,8 f,8 a,8 d,8 c,4 | \acciaccatura { d,8 } <d, f, a,>4\arpeggio f,8 a,8 f,8 a,8 b,4 | \acciaccatura { a,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 e,4 | \acciaccatura { e,8 } <d, f, a,>4\arpeggio f,8 a,8 f,8 a,8 e,4 | \acciaccatura { d,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 d,4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 g,4 | \acciaccatura { g,,8 } <g, b, c e>4\arpeggio b,8 c8 e8 b,8 d,4 | \acciaccatura { c,8 } <c, e, g,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
