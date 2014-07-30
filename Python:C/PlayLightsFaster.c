/*
    Simple udp server
    Silver Moon (m00n.silv3r@gmail.com)
*/
#include <stdio.h> //printf
#include <string.h> //memset
#include <stdlib.h> //exit(0);
#include <math.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include "lpd8806led.h"
#include <fcntl.h>
#include <unistd.h>

#define BUFLEN 512  //Max length of buffer
#define PORT 8888   //The port on which to listen for incoming data
 


void die(char *s)
{
    perror(s);
    exit(1);
}
 int isLight(int i, int height[]){
    
    if(i < 32 && i <= height[0]) return 1;
    if(i < 32) return 0;
    if(i >= 32 && i < 64 && i < 64 - height[1]) return 0;
    if(i >= 32 && i < 64 && i >= 64 - height[1]) return 1;
    if(i > 64 && i < 95 && i <= height[2] + 64) return 1;
    if(i > 64 && i < 95 && i < height[2] + 64) return 0;
    if(i >= 95 && i < 127 && i < 127 - height[3]) return 0;
    if(i >= 95 && i < 127 && i >= 127 - height[3]) return 1;
    if(i >=127 && i < 127 + height[4]) return 1;
    if(i >= 127 && i > 127 + height[4]) return 0;
    return 0;
}
int whatColorR(float a){
    int r = 0;
    int c = round(a);
    if(c < 0) c=0;
    if(c > 384) c = 384;
    if(c < 128){
        r = 127 - c % 128;
    }else if(c < 256){
        r = 0;
    }else{
        r = c % 128;
    }
    return r;
    
}
int whatColorG(float a){
    int g = 0;
    int c = round(a);
    if(c < 0) c=0;
    if(c > 384) c = 384;
    if(c < 128){
        g = c % 128;
    }else if(c < 256){
        g = 127 - c % 128;
    }else{
        g = 0;
    }
    return g;
    
}
int whatColorB(float a){
    int b = 0;
    int c = round(a);
    if(c < 0) c=0;
    if(c > 384) c = 384;
    if(c < 128){
        b = 0;
    }else if(c < 256){
        b = c % 128;
    }else{
        b = 127 - c % 128;
    }
    return b;
}
int main(void)
{
    int *r,*g,*b = 0;
    int height[5];
    int GPIOLEN = 4;
    int fd;              /* SPI device file descriptor */
    const int leds = 160; /* 50 LEDs in the strand */
    lpd8806_buffer buf;      /* Memory buffer for pixel values */
    int count;           /* Count of iterations (up to 3) */
    int i;               /* Counting Integer */
    set_gamma(2.5,2.5,2.5);
    /* Open SPI device */
    fd = open("/dev/spidev0.0",O_WRONLY);
    if(fd<0) {
        /* Open failed */
        fprintf(stderr, "Error: SPI device open failed.\n");
        exit(1);
    }

    /* Initialize SPI bus for lpd8806 pixels */
    if(spi_init(fd)<0) {
        /* Initialization failed */
        fprintf(stderr, "Unable to initialize SPI bus.\n");
        exit(1);
    }

    /* Allocate memory for the pixel buffer and initialize it */
    if(lpd8806_init(&buf,leds)<0) {
        /* Memory allocation failed */
        fprintf(stderr, "Insufficient memory for pixel buffer.\n");
        exit(1);
    }
    struct sockaddr_in si_me, si_other;
     
    int s,  slen = sizeof(si_other) , recv_len;
    char buff[BUFLEN];
     
    //create a UDP socket
    if ((s=socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1)
    {
        die("socket");
    }
     
    // zero out the structure
    memset((char *) &si_me, 0, sizeof(si_me));
     
    si_me.sin_family = AF_INET;
    si_me.sin_port = htons(PORT);
    si_me.sin_addr.s_addr = htonl(INADDR_ANY);
     
    //bind socket to port
    if( bind(s , (struct sockaddr*)&si_me, sizeof(si_me) ) == -1)
    {
        die("bind");
    }
    printf("Waiting for data...\n");
    //keep listening for data
    int iter;
    float c = 0;
    while(1)
    {
        //printf("Waiting for data...");
        fflush(stdout);

        //try to receive some data, this is a blocking call
        if ((recv_len = recvfrom(s, buff, BUFLEN, 0, (struct sockaddr *) &si_other, &slen)) == -1)
        {
            die("recvfrom()");
        }   
        
        GPIOLEN = 4;
        height[GPIOLEN] = atoi(strtok(buff,","));
        GPIOLEN --; 
        while(GPIOLEN > -1){
            height[GPIOLEN] = atoi(strtok(NULL,","));
            GPIOLEN--;
        }
        
        
        for(i = 0; i < leds;i++){
            write_gamma_color(&buf.pixels[i],isLight(i, height) * whatColorR(c), isLight(i, height) * whatColorG(c),isLight(i, height) * whatColorB(c));
        }
        memset(height,0,5);
        memset(buff,0,BUFLEN);
        if(send_buffer(fd,&buf)<0) {
        fprintf(stderr, "Error sending data.\n");
        
        exit(1);
        }
        c = c +.2;
        if(c>384) c = 0;
    }
    for(i=0;i<leds;i++) {
    write_gamma_color(&buf.pixels[i],0x00,0x00,0x00); 
    }
    send_buffer(fd,&buf);
    lpd8806_free(&buf);
    close(fd);
    close(s);
    return 0;
}