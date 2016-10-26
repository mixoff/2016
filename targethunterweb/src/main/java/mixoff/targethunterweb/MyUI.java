package mixoff.targethunterweb;

import javax.servlet.annotation.WebServlet;

import com.vaadin.annotations.Theme;
import com.vaadin.annotations.VaadinServletConfiguration;
import com.vaadin.server.ExternalResource;
import com.vaadin.server.VaadinRequest;
import com.vaadin.server.VaadinServlet;
import com.vaadin.ui.BrowserFrame;
import com.vaadin.ui.Button;
import com.vaadin.ui.Label;
import com.vaadin.ui.TextField;
import com.vaadin.ui.UI;
import com.vaadin.ui.VerticalLayout;

/**
 * This UI is the application entry point. A UI may either represent a browser window 
 * (or tab) or some part of a html page where a Vaadin application is embedded.
 * <p>
 * The UI is initialized using {@link #init(VaadinRequest)}. This method is intended to be 
 * overridden to add component to the user interface and initialize non-component functionality.
 */
@Theme("mytheme")
public class MyUI extends UI 
{

	private static final long serialVersionUID = 4475427316673356463L;

	@Override
    protected void init(VaadinRequest vaadinRequest) 
    {
        TargetIdentifier ti = new TargetIdentifier();
        MixoffServices mixoff = new MixoffServices();
        
        final VerticalLayout layout = new VerticalLayout();
        
        final TextField name = new TextField();
        name.setCaption("Enter target name:");

        Button button = new Button("Submit");
        button.addClickListener( e -> {
            layout.addComponent(new Label("Submitted: " + name.getValue() ));
            
            // Send name to an identity generator - generate a picture
            ti.generateImageUrl(name.getValue());
            
            // Pass image to identify service https://mixoff-identity-test.eu-gb.mybluemix.net/identify
            final Label identification = new Label("Identification Result: " + mixoff.identify(ti.getImageUrl()));
            
            
            // Pass image to analyse service https://mixoff-identity-test.eu-gb.mybluemix.net/analyse
            final Label analysis = new Label("Analysis Result: " + mixoff.analyse(ti.getImageUrl()));

            
            layout.addComponents(identification, analysis);
            
            BrowserFrame browser = new BrowserFrame(ti.getImageUrl(),
            	    new ExternalResource(ti.getImageUrl()));
            	browser.setWidth("150px");
            	browser.setHeight("200px");
            	layout.addComponent(browser);
        });
        
        
        

        
        
        
        layout.addComponents(name, button);
        layout.setMargin(true);
        layout.setSpacing(true);
        
        setContent(layout);
    }

    @WebServlet(urlPatterns = "/*", name = "MyUIServlet", asyncSupported = true)
    @VaadinServletConfiguration(ui = MyUI.class, productionMode = false)
    public static class MyUIServlet extends VaadinServlet 
    {
    }
}
