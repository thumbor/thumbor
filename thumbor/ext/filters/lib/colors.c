
void
rgb2ycbcr(float *r, float *g, float *b)
{
    static float y, cb, cr;
    y = 0.2990 * *r + 0.5870 * *g + 0.1140 * *b;
    cb = -0.1687 * *r - 0.3313 * *g + 0.5000 * *b + 128.0;
    cr = 0.5000 * *r - 0.4187 * *g - 0.0813 * *b + 128.0;
    *r = y;
    *g = cb;
    *b = cr;
}

void
ycbcr2rgb(float *y, float *cb, float *cr)
{
    static float r, g, b;
    r = *y + 1.40200 * (*cr - 128.0);
    g = *y - 0.34414 * (*cb - 128.0) - 0.71414 * (*cr - 128.0);
    b = *y + 1.77200 * (*cb - 128.0);
    *y = r;
    *cb = g;
    *cr = b;
}
