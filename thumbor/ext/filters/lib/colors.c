
void
rgb2ycbcr(float *r, float *g, float *b)
{
    static float y, cb, cr;
    y = 0.2990f * *r + 0.5870f * *g + 0.1140f * *b;
    cb = -0.1687f * *r - 0.3313f * *g + 0.5000f * *b + 128.0f;
    cr = 0.5000f * *r - 0.4187f * *g - 0.0813f * *b + 128.0f;
    *r = y;
    *g = cb;
    *b = cr;
}

void
ycbcr2rgb(float *y, float *cb, float *cr)
{
    static float r, g, b;
    r = *y + 1.40200f * (*cr - 128.0f);
    g = *y - 0.34414f * (*cb - 128.0f) - 0.71414f * (*cr - 128.0f);
    b = *y + 1.77200f * (*cb - 128.0f);
    *y = r;
    *cb = g;
    *cr = b;
}
