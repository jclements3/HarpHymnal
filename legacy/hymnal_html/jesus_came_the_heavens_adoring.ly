\version "2.22.1"

\header {
  title = "124  Jesus Came, the Heavens Adoring"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key b \minor
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf fis'4 b'4 b'4 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } g'8 fis'4 d'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } fis'4 b'4 a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" } } } g'4 fis'2 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } e'4 e'4 cis'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } e'4 fis'4 fis'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } aes'4 a'4 \acciaccatura { cis''16 a'16 } b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } g'4 fis'2 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } cis''4 d''4 cis''8 b'8 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } b'4 cis''4 fis'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } cis''8 b'8 bes'4 b'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'4 \acciaccatura { cis''16 a'16 } b'2 | }
    { \voiceTwo <b d'>1\p\arpeggio | <a b>1\arpeggio | <a b d'>1\arpeggio | <cis d fis a>1\arpeggio | <cis e g>1\arpeggio | b1 | <g b d'>1\arpeggio | <fis a cis'>1\arpeggio | <cis' d' fis' a'>1\arpeggio | <cis' d' a'>1\arpeggio | <e' a'>1\arpeggio | <e a cis'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { b,,8 } <g b d'>1\p\arpeggio | \acciaccatura { d,8 } <b, cis e g>4\arpeggio cis8 e8 g8 cis8 e4 | \acciaccatura { d,8 } <b, cis e g>4\arpeggio cis8 e8 g8 cis8 fis4 | \acciaccatura { e,8 } <cis e g b>4\arpeggio e8 g8 b8 e8 fis4 | \acciaccatura { e,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 e4 | \acciaccatura { d,8 } <g b d'>4\arpeggio b8 d'8 b8 d'8 cis'4 | \acciaccatura { b,,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 d4 | \acciaccatura { fis,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 g4 | \acciaccatura { fis,8 } <d fis g b>4\arpeggio fis8 g8 b8 fis8 d4 | \acciaccatura { fis,8 } <d fis g b>4\arpeggio fis8 g8 b8 fis8 cis4 | \acciaccatura { b,,8 } <g b d'>4\arpeggio b8 d'8 b8 d'8 cis'4 | \acciaccatura { b,,8 } <g b d'>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
