\version "2.22.1"

\header {
  title = "273  Twas In The Moon of Wintertime"
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
    { \voiceOne fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } }\mf b'4 cis''4 d''4 | e''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } d''4 cis''4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } b'4 b'4 cis''4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } \acciaccatura { cis''16 a'16 } b'2. | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } b'4 cis''4 d''4 | e''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } d''4 cis''4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } b'4 b'4 cis''4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "2" } } } \acciaccatura { cis''16 a'16 } b'2. | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } fis''4 fis''4 cis''4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } e''4. d''8 cis''4 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } d''4 cis''4 \acciaccatura { cis''16 a'16 } b'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } cis''4. b'8 b'4 | \acciaccatura { b'16 g'16 } a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } b'4 b'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 \acciaccatura { g'16 e'16 } fis'2 | b'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 fis'4 | b'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } b'4 \acciaccatura { d''16 b'16 } cis''4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } e''4 fis''4 fis'4 | \acciaccatura { cis''16 a'16 } b'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } | }
    { \voiceTwo g'1\p | <cis' d' fis' a'>1\arpeggio | <g b d'>1\arpeggio | <g b d'>1\arpeggio | g'1 | <cis' d' fis' a'>1\arpeggio | <g b d'>1\arpeggio | <fis g b d'>1\arpeggio | <g' d''>1\arpeggio | <g' b'>1\arpeggio | g'1 | <fis' a'>1\arpeggio | <g b d'>1\arpeggio | <b d'>1\arpeggio | <b d'>1\arpeggio | <e a cis'>1\arpeggio | <e' a'>1\arpeggio | <e' a' cis''>1\arpeggio | <e a cis'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { fis,8 } <d fis a>1\p\arpeggio | \acciaccatura { b,,8 } <d fis g b>4\arpeggio fis8 g8 b8 fis8 g4 | \acciaccatura { fis,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 cis4 | \acciaccatura { b,,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 d4 | \acciaccatura { fis,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 cis4 | \acciaccatura { b,,8 } <d fis g b>4\arpeggio fis8 g8 b8 fis8 g4 | \acciaccatura { fis,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 cis4 | \acciaccatura { b,,8 } <g b cis' e'>4\arpeggio b8 cis'8 e'8 b8 g4 | \acciaccatura { e,8 } <cis e g>4\arpeggio e8 g8 e8 g8 cis4 | \acciaccatura { b,,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 cis4 | \acciaccatura { b,,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 d4 | \acciaccatura { fis,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 g4 | \acciaccatura { fis,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 d4 | \acciaccatura { b,,8 } <g b d'>4\arpeggio b8 d'8 b8 d'8 e4 | \acciaccatura { d,8 } <g b d'>4\arpeggio b8 d'8 b8 d'8 g4 | \acciaccatura { b,,8 } <g b d'>4\arpeggio b8 d'8 b8 d'8 cis'4 | \acciaccatura { b,,8 } <g b d'>4\arpeggio b8 d'8 b8 d'8 g4 | \acciaccatura { b,,8 } <g b d'>4\arpeggio b8 d'8 b8 d'8 cis'4 | \acciaccatura { b,,8 } <g b d'>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
