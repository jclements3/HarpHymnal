\version "2.22.1"

\header {
  title = "145  Lift High The Cross"
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
    { \voiceOne g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf c''4. g'8 | f'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } \acciaccatura { a'16 fis'16 } g'4 | e'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'8 g'4 a'4 | d'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } \acciaccatura { e'16 c'16 } d'4 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "Vii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } g'4 c''2 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } a'4 \acciaccatura { a'16 fis'16 } g'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 f'8 e'8 d'4 | c'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } fis'4. e'8 | fis'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } \acciaccatura { e'16 c'16 } d'2 | e'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } fis'8 g'4 a'4 | b'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'2 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } b'4 a'4 | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } \acciaccatura { e'16 c'16 } d'2 | e'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'8 g'4 fis'4 | \acciaccatura { a'16 fis'16 } g'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <c' e'>1\p\arpeggio | <fis g b d'>1\arpeggio | c'1 | <fis g b>1\arpeggio | <a d' fis'>1\arpeggio | <e' b'>1\arpeggio | <fis a c'>1\arpeggio | <fis a>1\arpeggio | <e g b>1\arpeggio | <d fis a>1\arpeggio | c'1 | <b d' fis'>1\arpeggio | <a c' e'>1\arpeggio | <fis' g' b'>1\arpeggio | c'1 | <c' e'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { c,8 } <g, b, d>1\p\arpeggio | \acciaccatura { g,,8 } <g, b, c e>4\arpeggio b,8 c8 e8 b,8 g,4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, c e>4\arpeggio b,8 c8 e8 b,8 g,4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 e8 g8 d4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { e,8 } <e g b>4\arpeggio g8 b8 g8 b8 g4 | \acciaccatura { fis,8 } <e g b>4\arpeggio g8 b8 g8 b8 fis4 | \acciaccatura { e,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 e4 | \acciaccatura { d,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { c,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 c4 | \acciaccatura { b,,8 } <a, c e>4\arpeggio c8 e8 c8 e8 b,4 | \acciaccatura { a,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, c e>4\arpeggio b,8 c8 e8 b,8 g,4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
