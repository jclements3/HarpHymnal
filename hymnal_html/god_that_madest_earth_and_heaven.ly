\version "2.22.1"

\header {
  title = "082  God, That Madest Earth and Heaven"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key g \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne g'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" } } }\mf fis'8 e'4 g'4 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" "7" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'8 fis'4 d'4 | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "6" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'4. fis'8 | \acciaccatura { a'16 fis'16 } g'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" } } } | g'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" } } } fis'8 e'4 g'4 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" "7" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'8 fis'4 d'4 | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "6" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'4. fis'8 | \acciaccatura { a'16 fis'16 } g'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "²+8" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } b'4 c''4 d''4 | e''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "6" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''4 c''4 b'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" } } } b'4 a'4 g'4 | b'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" } } } a'8 g'4 \acciaccatura { g'16 e'16 } fis'4 | g'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" } } } fis'8 e'4 g'4 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" "7" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'8 fis'4 d'4 | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "6" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'4. fis'8 | \acciaccatura { a'16 fis'16 } g'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "+8" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <a c'>1\p\arpeggio | r1 | <g b d'>1\arpeggio | <a c' e'>1\arpeggio | <a c'>1\arpeggio | r1 | <g b d'>1\arpeggio | <c' e'>1\arpeggio | <d' fis' a'>1\arpeggio | g'1 | <a c' e'>1\arpeggio | <a c' e'>1\arpeggio | <a c'>1\arpeggio | r1 | <g b d'>1\arpeggio | <g b d'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <g, b, d>1\p\arpeggio | \acciaccatura { a,,8 } <a, c e g>4\arpeggio c8 e8 g8 c8 e4 | \acciaccatura { d,8 } <d fis a b>4\arpeggio fis8 a8 b8 fis8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 g,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 b,4 | \acciaccatura { a,,8 } <a, c e g>4\arpeggio c8 e8 g8 c8 e4 | \acciaccatura { d,8 } <d fis a b>4\arpeggio fis8 a8 b8 fis8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 g,4 | \acciaccatura { c,8 } <g, c e g>4\arpeggio c8 e8 g8 c8 e4 | \acciaccatura { d,8 } <d fis a b>4\arpeggio fis8 a8 b8 fis8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 b,4 | \acciaccatura { a,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 g,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 b,4 | \acciaccatura { a,,8 } <a, c e g>4\arpeggio c8 e8 g8 c8 e4 | \acciaccatura { d,8 } <d fis a b>4\arpeggio fis8 a8 b8 fis8 a,4 | \acciaccatura { g,,8 } <g, b, d>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
