package mixoff.targethunterweb;

import java.awt.image.BufferedImage;
import java.awt.image.RenderedImage;
import java.io.File;
import java.io.IOException;

import javax.imageio.ImageIO;

public class TargetIdentifier {

	private BufferedImage image;
	private String imageUrl;
	
	void generateImageUrl(String value) 
	{	
		// TODO: Implement properly
		imageUrl = getKevinBacon();
	}

	private String getKevinBacon()
	{
		String url = "";

	    //img = ImageIO.read(new File("bacon3.jpg"));
		url = "http://blogs.longwood.edu/jameslaycock/files/2015/03/19_Kevin_Bacon.jpg";

		//return new BufferedImage(500, 500, BufferedImage.TYPE_INT_RGB);
		return url;
	}

	RenderedImage getImage() 
	{	
		return image;
	}
	
	String getImageUrl()
	{
		return imageUrl;
	}

}
