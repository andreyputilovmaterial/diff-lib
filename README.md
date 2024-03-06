# diff-lib
Taking part out of mdm-diff to have it stored as a separate library that can be re-used.

Basically, this is just a Myers diff implementation.

TODO:
- Investigate that bug when I had to add an empty item in the beginning
- - to do that, I need to introduce some subsystem for testing
- Check splitting the string into parts. It seems MyersDiffSplitter is working correctly and giving properly separated parts, but then pieces are treated as chars anyway
- Find proper length for arrays when allocating
