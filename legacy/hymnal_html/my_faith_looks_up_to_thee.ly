\version "2.22.1"

\header {
  title = "163  My Faith Looks Up To Thee"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key d \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne d'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf fis'4 a'4 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'8 \acciaccatura { g'16 e'16 } fis'2 | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } e'4 g'4 | g'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } fis'8 e'2 | fis'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } e'4 \acciaccatura { cis''16 a'16 } b'4 | a'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } fis'4 \acciaccatura { a'16 fis'16 } g'4 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } b'8 a'2 | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } fis'4 g'4 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } b'8 a'2 | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } cis''4 b'4 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'8 fis'4 \acciaccatura { e'16 cis'16 } d'4 | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } a'2 | \acciaccatura { e'16 cis'16 } d'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo r1 | d'1 | <fis b d'>1\arpeggio | <g a cis'>1\arpeggio | <d' a'>1\arpeggio | <d' fis'>1\arpeggio | d'1 | <d' fis'>1\arpeggio | d'1 | <d' fis'>1\arpeggio | <d' fis' a'>1\arpeggio | r1 | <g a cis'>1\arpeggio | <g b>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <a, cis e>1\p\arpeggio | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 a,4 | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 b,4 | \acciaccatura { a,,8 } <a, cis d fis>4\arpeggio cis8 d8 fis8 cis8 e,4 | \acciaccatura { d,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 a,4 | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 e,4 | \acciaccatura { d,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 b,4 | \acciaccatura { d,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 e4 | \acciaccatura { d,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 e4 | \acciaccatura { d,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 cis4 | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 e4 | \acciaccatura { d,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 a,4 | \acciaccatura { a,,8 } <a, cis d fis>4\arpeggio cis8 d8 fis8 cis8 e,4 | \acciaccatura { d,8 } <d, fis, a,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
