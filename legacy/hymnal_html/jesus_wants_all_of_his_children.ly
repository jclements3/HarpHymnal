\version "2.22.1"

\header {
  title = "134  Jesus Wants All Of His Children"
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
    { \voiceOne fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } }\mf fis'4 fis'4 e'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'4 b'4 a'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''4 d''4 a'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } e'4 \acciaccatura { fis'16 d'16 } e'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 a'4 b'4 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } d''4 fis'4 e'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } fis'4 e'4 d'4 | r1 | }
    { \voiceTwo <cis e g a>1\p\arpeggio | <g b>1\arpeggio | fis'1 | <d fis a>1\arpeggio | <fis a cis'>1\arpeggio | a'1 | cis'1 | <cis' e' g'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <d, fis, a, b,>1\p\arpeggio | \acciaccatura { d,8 } <d, fis, a,>4\arpeggio fis,8 a,8 fis,8 a,8 e,4 | \acciaccatura { d,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 b,4 | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 a,4 | \acciaccatura { d,8 } <d, fis, a,>4\arpeggio fis,8 a,8 fis,8 a,8 g,4 | \acciaccatura { fis,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 fis,4 | \acciaccatura { e,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 fis,4 | \acciaccatura { e,8 } <e, g, b,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
